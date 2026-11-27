#!/usr/bin/env python3
"""Holds the compiler to perl 5.42 over generated double-quoted strings
with references in them (step 13d; D111, D114, T247, T253). Written by the
builder, after the method of step 11a's review (briefs/step11a-review/):
where perl ends a variable in a string is the danger, so every string the
compiler takes is run beside perl.

For every string, the compiler's verdict (classify.ts):

  taken, and perl prints it in silence   the compiled program must print
                                         exactly that; or, if it faults, the
                                         fault is counted by its message (a
                                         LOUD, to be read: each must be a
                                         decision's, D107 or D112)
  taken, and perl warns or dies          the compiled program must fault
  taken, and perl prints an address      the compiled program must fault
                                         (D112)
  refused                                counted by the compiler's message,
                                         and by whether perl ran it in silence

    python3 docs/briefs/step13d-review/strings.py [MODE ...]

MODE is valid (every chain that reaches something in the program's data,
written every way, with what may follow it), exhaustive (heads and links
of every kind, two deep), braces, random (default: all four). Of the
strings the compiler takes in a mode, SAMPLE (12,000) at most are run. Work files go to
$REVIEW_TMP (default ./tmp beside this file). Exit 1 if anything differs.
"""

import collections
import itertools
import json
import os
import random
import re
import subprocess
import sys
import functools
from multiprocessing import Pool

print = functools.partial(print, flush=True)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
PERL = os.environ.get('CURLY_PERL', '/opt/perl-5.42/bin/perl')
TMP = os.environ.get('REVIEW_TMP', os.path.join(HERE, 'tmp'))
SEP = '=#=#='
SAMPLE = int(os.environ.get('SAMPLE', '12000'))

# What the program declares: references of every kind at every depth, an
# array and a hash of the names $a and $h, and plain scalars.
HEADER = '''use v5.42;
my $x = "X";
my $i = 1;
my $k = "k";
my $u;
my @x = ("p", "q");
my @a = ([1, 2], {k => "ak"}, 3);
my %h = (k => [4, 5], a => {k => "hak", b => [6]});
my $r = [7, [8, 9], {k => "rk", a => [10]}, "s"];
my $q = {k => "qk", a => [11, 12], b => {k => [13]}};
my $sv = "sv";
my $s = \\$sv;
my $t = \\$r;
my $e = [];
'''
# Each string is printed in a block of its own that declares all of it
# again, on one line: perl makes what a read goes through, in silence, and
# a string after it would see what an earlier one made.
DECLARE = ' '.join(HEADER.split('\n')[1:]).strip()
LINES_BEFORE = 1

HEADS = ['$r', '$q', '$a[0]', '$a[1]', '$a[2]', '$h{k}', '$h{a}', '$x', '$s', '$t', '$u', '$e', '$i']
LINKS = ['->[0]', '->[1]', '->[$i]', '->[-1]', '->[2]', '->[9]', '[0]', '[1]', '[$i]', '[-1]',
         '{k}', '{a}', '{$k}', '{b}', '->{k}', '->{a}', '->{$k}', '->{b}',
         '->@*', '->$#*', '->$*', '->@[0, 1]', '->@[0 .. 1]', '->@[1,]', '->@{k}', '->%*']
SUFFIXES = ['', ' ', 'x', '-', '->', '->x', '->[', '->{', '->@', '->$', '->%', '->@x', '->$x', '[', '{', '[0]', '{k}',
            '::', '::x', '}', ']', '*', '@x', '$x', '\\n', ' [0]', '->[0]', '->{k}', '->@*', '->$*', '[01]', '{ k }',
            '[ 1 ]', '{1}', '{-k}', '[$i+1]', '[x]', '{k}[0]']


def exhaustive():
    out = []
    for head in HEADS:
        for n in range(3):
            for links in itertools.product(LINKS, repeat=n):
                for suffix in SUFFIXES if n < 2 else SUFFIXES[:12]:
                    out.append('<' + head + ''.join(links) + suffix + '>')
    return out


def braces():
    out = []
    inner = []
    for head in HEADS:
        inner.append(head)
        for a in LINKS[:18]:
            inner.append(head + a)
            for b in LINKS[:18:3]:
                inner.append(head + a + b)
    for sigil in ['@', '$', '$#']:
        for body in inner:
            for pad in [('', ''), (' ', ' '), ('', ' '), ('  ', '')]:
                for suffix in ['', 'x', '[0]', '{k}', '->[0]', '->{k}', '->@*', '->x', ' [0]', '::x', '}']:
                    out.append('<' + sigil + '{' + pad[0] + body + pad[1] + '}' + suffix + '>')
    # what is not a variable in the braces
    for sigil in ['@', '$', '$#']:
        for body in ['$r ->[1]', '$r [1]', '$r->[1] ->[0]', '[1, 2]', '\\$x', ' [1]', ' \\$x', 'x', ' x ', '$r, $q', '$r->@*',
                     '$r->[0]->@*', '"$r"', '$$t', '$r->[$i+1]', '{}', '', '$r->[01]', '$q->{"k"}', '$q->{k k}']:
            out.append('<' + sigil + '{' + body + '}>')
    return out


# The program's data, as Python sees it, so that chains that reach
# something can be written out: every way down from every head.
DATA = {
    '$r': [7, [8, 9], {'k': 'rk', 'a': [10]}, 's'],
    '$q': {'k': 'qk', 'a': [11, 12], 'b': {'k': [13]}},
    '@a': [[1, 2], {'k': 'ak'}, 3],
    '%h': {'k': [4, 5], 'a': {'k': 'hak', 'b': [6]}},
    '$t': 'SCALARREF',
    '$s': 'SCALAR',
}


def spellings(name, value, depth=3):
    """Every chain from a head, written every way: (text, what it reaches)."""
    head = {'@a': '$a', '%h': '$h'}.get(name, name)
    out = []

    def walk(text, v, n, first):
        if n:
            out.append((text, v))
        if n == depth:
            return
        arrows = ['->'] if first and head not in ('$a', '$h') else [''] if first else ['', '->']
        if isinstance(v, list):
            for i, x in enumerate(v):
                forms = {str(i)} | ({'$i'} if i == 1 else set()) | ({'-1'} if i == len(v) - 1 else set())
                for f in sorted(forms):
                    for a in arrows:
                        walk(text + a + '[' + f + ']', x, n + 1, False)
        elif isinstance(v, dict):
            for k in sorted(v):
                for f in sorted({k} | ({'$k'} if k == 'k' else set())):
                    for a in arrows:
                        walk(text + a + '{' + f + '}', v[k], n + 1, False)

    walk(head, value, 0, True)
    if name[0] == '$':
        out.append((head, value))
    return out


POSTFIX = ['->@*', '->$#*', '->$*', '->@[0, 1]', '->@[0 .. 1]', '->@[1,]', '->@[-1]', '->@[$i]']
BAD = ['->[0]', '[0]', '->{k}', '{k}', '[9]', '{z}', '->[9][0]', '->{z}{k}', '->@*', '->$*']


def valid():
    out = []
    for name, value in DATA.items():
        for text, v in spellings(name, value):
            for suffix in SUFFIXES:
                out.append('<' + text + suffix + '>')
            for post in POSTFIX:
                for suffix in ['', 'x', ' [0]', '->x', '::x', '[0]', '->[0]', '{k}']:
                    out.append('<' + text + post + suffix + '>')
            for bad in BAD:
                out.append('<' + text + bad + '>')
            for sigil in ['@', '$', '$#']:
                for pad in [('', ''), (' ', ' '), ('', '  ')]:
                    for suffix in ['', 'x', '[0]', '{k}', '->[0]', '->{k}', '->@*', '->x', ' [0]', '::x', '}']:
                        out.append('<' + sigil + '{' + pad[0] + text + pad[1] + '}' + suffix + '>')
    out += ['<${$s}>', '<${ $t }>', '<$t->$*>', '<${$t}>', '<$s->$*>', '<@{${$t}}>']
    return out


ALPHABET = ['$r', '$q', '$a', '$h', '$x', '$s', '$t', '$i', '$k', '@', '$', '$#', '%', '->', '-', '>', '[', ']', '{', '}',
            '0', '1', '-1', 'k', 'a', '*', '@*', '$*', '$#*', ' ', ',', '..', '::', ':', '\\', 'x', '[0]', '{k}', '{a}', '[$i]',
            '{$k}', '@{', '${', '$#{', '@x', '$x']


def rand(n, seed):
    g = random.Random(seed)
    out = set()
    while len(out) < n:
        out.add('<' + ''.join(g.choice(ALPHABET) for _ in range(g.randint(1, 7))) + '>')
    return sorted(out)


def classify(bodies):
    out = []
    for k in range(0, len(bodies), 20000):
        ask = json.dumps({'header': HEADER, 'bodies': bodies[k:k + 20000]})
        r = subprocess.run(['node', os.path.join(HERE, 'classify.ts')], input=ask, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-2000:]
        out += json.loads(r.stdout)
    return out


ADDRESS = re.compile(r'(ARRAY|HASH|SCALAR|REF|CODE)\(0x[0-9a-f]+\)')


def program(bodies):
    return 'use v5.42;\n' + ''.join(f'{{ {DECLARE} print "{b}"; print "\\n{SEP}\\n"; }}\n' for b in bodies)


def compile_run(src, tag):
    path = os.path.join(TMP, f'{tag}.pl')
    open(path, 'w').write(src)
    exe = os.path.join(TMP, tag)
    c = subprocess.run(['node', os.path.join(ROOT, 'bin', 'curlyc.ts'), '-o', exe, path], capture_output=True, text=True)
    if c.returncode != 0:
        return None, c.stderr
    r = subprocess.run([exe], capture_output=True, timeout=120)
    return r, path


def batch(args):
    """One batch of taken strings: what perl complains of, what it prints an
    address for, and what the compiled program makes of the rest."""
    n, bodies = args
    tag = f'b{os.getpid()}-{n}'
    complained, addressed, loud, wrong, same = [], [], [], [], 0
    bodies = list(bodies)
    while True:
        path = os.path.join(TMP, f'{tag}.pl')
        open(path, 'w').write(program(bodies))
        p = subprocess.run([PERL, path], capture_output=True, timeout=120)
        err = p.stderr.decode('utf-8', 'replace')
        if not err and p.returncode == 0:
            break
        named = sorted(set(int(m) for m in re.findall(r' line (\d+)', err)))
        assert named, err[:300]
        out = {m - LINES_BEFORE - 1 for m in named if 0 <= m - LINES_BEFORE - 1 < len(bodies)}
        assert out, err[:300]
        complained += [(bodies[m], err.strip().split('\n')[0]) for m in sorted(out)]
        bodies = [b for m, b in enumerate(bodies) if m not in out]
    theirs = p.stdout.decode('utf-8', 'replace').split(f'\n{SEP}\n')
    keep = []
    for m, b in enumerate(bodies):
        (addressed if ADDRESS.search(theirs[m]) else keep).append(b)
    bodies = keep
    while bodies:
        expected = subprocess.run([PERL, '-e', program(bodies)], capture_output=True, timeout=120).stdout.decode('utf-8', 'replace').split(f'\n{SEP}\n')
        r, path = compile_run(program(bodies), tag)
        if r is None:
            wrong.append(('A BATCH DOES NOT COMPILE', path[:300], ''))
            break
        ours = r.stdout.decode('utf-8', 'replace').split(f'\n{SEP}\n')
        done = len(ours) - 1
        for m in range(min(done, len(bodies))):
            if ours[m] != expected[m]:
                wrong.append(('DIFFERS', bodies[m], f'perl {expected[m]!r}, compiled {ours[m]!r}'))
            else:
                same += 1
        if r.returncode == 0 and not r.stderr:
            break
        f = re.match(rb'fault: (.*?) at \S+ line (\d+)\.\n', r.stderr)
        if f is None:
            wrong.append(('STOPPED', bodies[done] if done < len(bodies) else '?', r.stderr.decode()[:200]))
            break
        m = int(f.group(2)) - LINES_BEFORE - 1
        if m != done:
            wrong.append(('A FAULT ON ANOTHER LINE', bodies[done], r.stderr.decode()[:200]))
            break
        loud.append((bodies[m], f.group(1).decode()))
        bodies = bodies[m + 1:]
    for f in (tag, tag + '.pl', tag + '.c', tag + '.rt.o'):
        if os.path.exists(os.path.join(TMP, f)):
            os.remove(os.path.join(TMP, f))
    return complained, addressed, loud, wrong, same


def alone(args):
    """A string perl complains of, or prints an address for: the compiled
    program must fault."""
    n, body = args
    r, path = compile_run(program([body]).replace(f' print "\\n{SEP}\\n";', ''), f'a{os.getpid()}-{n}')
    if r is None:
        return (body, 'refused after all: ' + path.strip()[-120:])
    for f in (f'a{os.getpid()}-{n}', f'a{os.getpid()}-{n}.pl', f'a{os.getpid()}-{n}.c'):
        if os.path.exists(os.path.join(TMP, f)):
            os.remove(os.path.join(TMP, f))
    if r.returncode == 1 and r.stderr.startswith(b'fault: ') and r.stdout == b'':
        return None
    return (body, f'runs: exit {r.returncode}, {r.stdout[:80]!r} {r.stderr[:80]!r}')


def perl_silent(bodies):
    """Of strings the compiler refuses, which perl runs in silence."""
    silent = set()
    for k in range(0, len(bodies), 1000):
        group = bodies[k:k + 1000]
        while group:
            path = os.path.join(TMP, 'refused.pl')
            open(path, 'w').write(program(group))
            p = subprocess.run([PERL, path], capture_output=True, timeout=120)
            err = p.stderr.decode('utf-8', 'replace')
            if not err and p.returncode == 0:
                silent.update(group)
                break
            named = sorted(set(int(m) for m in re.findall(r' line (\d+)', err)))
            out = {m - LINES_BEFORE - 1 for m in named if 0 <= m - LINES_BEFORE - 1 < len(group)}
            if not out:
                # perl stops before it says a line of ours (a string that
                # never ends): try each alone.
                for b in group:
                    q = subprocess.run([PERL, '-e', program([b])], capture_output=True, timeout=30)
                    if q.returncode == 0 and not q.stderr:
                        silent.add(b)
                break
            group = [b for m, b in enumerate(group) if m not in out]
    return silent


def hold(bodies, tag, alone_sample=600):
    os.makedirs(TMP, exist_ok=True)
    bodies = sorted(set(bodies))
    verdicts = classify(bodies)
    taken = [b for b, v in zip(bodies, verdicts) if 'ok' in v]
    if len(taken) > SAMPLE:
        print(f'  of the {len(taken)} taken, {SAMPLE} picked at random are run')
        taken = sorted(random.Random(5).sample(taken, SAMPLE))
    refused = [(b, v['no']) for b, v in zip(bodies, verdicts) if 'no' in v]
    print(f'{tag}: {len(bodies)} strings, the compiler takes {len(taken)} and refuses {len(refused)}')
    groups = [taken[k:k + 200] for k in range(0, len(taken), 200)]
    complained, addressed, loud, wrong, same = [], [], [], [], 0
    with Pool(4) as pool:
        for done, (c, a, l, w, s) in enumerate(pool.imap_unordered(batch, list(enumerate(groups)))):
            if done % 10 == 9:
                print(f'  {done + 1} of {len(groups)} batches')
            complained += c
            addressed += a
            loud += l
            wrong += w
            same += s
        g = random.Random(13)
        tried = g.sample(complained, min(alone_sample, len(complained))) + g.sample([(b, '') for b in addressed], min(alone_sample, len(addressed)))
        missed = [x for x in pool.imap_unordered(alone, [(n, b) for n, (b, _) in enumerate(tried)]) if x is not None]
    print(f'  {same} print what perl prints; {len(loud)} fault where perl prints in silence; '
          f'{len(complained)} perl warns of or dies at, {len(addressed)} perl prints an address for: '
          f'{len(tried)} of these two compiled alone, {len(tried) - len(missed)} fault')
    for why, n in collections.Counter(m for _, m in loud).most_common():
        example = next(b for b, m in loud if m == why)
        print(f'    LOUD {n}: {why}   e.g. {example}')
    # (A sample: perl stops at the first string it does not compile, so
    # each costs a run of its own.)
    asked = random.Random(17).sample(refused, min(3000, len(refused)))
    silent = perl_silent([b for b, _ in asked])
    reasons = collections.Counter(re.sub(r'\$\w+|\d+', 'N', why.split(':')[0])[:90] for b, why in refused if b in silent)
    print(f'  refused: {len(refused)}; of {len(asked)} asked, perl runs {len(silent)} in silence')
    for why, n in reasons.most_common(15):
        print(f'    stricter, {n}: {why}')
    for w in (wrong + [('DOES NOT FAULT',) + m for m in missed])[:30]:
        print('  WRONG', w)
    return len(wrong) + len(missed)


def main(modes):
    modes = modes or ['valid', 'exhaustive', 'braces', 'random']
    os.environ.setdefault('CURLY_RT_OBJ', os.path.join(TMP, 'rt.o'))
    os.makedirs(TMP, exist_ok=True)
    failed = 0
    for mode in modes:
        bodies = exhaustive() if mode == 'exhaustive' else braces() if mode == 'braces' else valid() if mode == 'valid' else rand(30000, 7)
        # (Every string is classified; of those the compiler takes, a
        # sample of SAMPLE is run beside perl, each run costing a compile.)
        failed += hold(bodies, mode)
    print('nothing differs' if not failed else f'{failed} DIFFER')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
