#!/usr/bin/env python3
"""More probes for the census (2026-11-27; D11, D96): other people's Perl
beyond import.py's three sources.

    python3 t/census/import_more.py PERL-SOURCE PVM PERL5-SON CHALK

PERL-SOURCE is perl 5.42.0's source unpacked (its pod/ is read); the rest
are checkouts. Run again when a source moves: it writes what is not there
and changes nothing that is. It appends its places to t/census/SOURCES.tsv
(import.py keeps them when it rewrites that file).

The sources, in the order names are given:

    pod/          every verbatim block of perl's pod/*.pod (not the
                  perl5*delta histories), and every run of verbatim
                  blocks with only blank lines between, as one program
    pvm-more/     pvm's .pl files outside conformance/mdtest (import.py's)
                  and testdata/perlonjava
    perlonjava/   PerlOnJava's unit tests as pvm carries them: a .t with no
                  Test:: module as it is; one that uses only Test::More's
                  ok, is, isnt, pass, fail, plan and done_testing,
                  rewritten (below)
    son-more/     perl5-son's .pl files outside import.py's two trees
    chalk-more/   Chalk's .pl files outside t/data/audit-probes

The rewrite of a Test::More file, statement by statement and nothing
else: `use Test::More ...;`, `plan ...;` and `done_testing...;` go;
`use strict;`, `use warnings;` and `use feature 'say';` go (each is what
`use v5.42;` already does); `is(GOT, WANT, ...);` and `isnt(...)` become
`say GOT;`, `ok(GOT, ...);` becomes `say((GOT) ? "ok" : "not ok");`, and
`pass(...)`/`fail(...)` `say "ok"`/`say "not ok"`. A file with any other
use of those words is left out.

A pod's example is written without strict, which `use v5.42;` turns on:
when perl's only complaint about one is globals not declared, a `my` of
each is put on the line after `use v5.42;`, the one change made to a
pod's text (`declared`).

Unlike import.py's sources, which were written as probes, these are kept
only when they are probes: a program is imported when, with `use v5.42;`
in front, perl 5.42 runs it plain with stdin empty, exits 0, writes
nothing on stderr, prints something to stdout, and prints the same under
the census's eight hash seeds; and when its text reads no file, the
environment, the clock, a process or the network, uses no module but strict,
warnings, utf8, feature and integer, and is 200 lines at most. Everything else is dropped, not put
in not-perl/. A program that is the same text as a probe already there,
in run/, by-design/ or not-perl/, is not imported again.
"""
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import checks  # noqa: E402

USE = 'use v5.42;\n'
# What a probe may not do: read a file, the environment, the clock, a
# process, the network, stdin; or load a module.
FORBIDDEN = re.compile(
    r'\b(open|opendir|readdir|close|binmode|sysopen|unlink|mkdir|rmdir|rename|chdir|stat|lstat|utime|chmod|chown|glob|'
    r'system|exec|fork|wait|waitpid|kill|qx|syscall|socket|connect|bind|listen|accept|getpw\w+|getgr\w+|gethost\w+|'
    r'time|times|localtime|gmtime|sleep|alarm|rand|srand|select|require|do\s+["\'$]|dbmopen|tie|caller|eval|'
    r'STDIN|ARGV|ENV|DATA|__FILE__|__LINE__)\b|`|\$\$|\$0\b|<\$?\w*>|-[erwxofdszl]\s+[$"\']')
USE_LINE = re.compile(r'^\s*(use|no)\s+([\w:]+)', re.M)
PRAGMAS = {'strict', 'warnings', 'utf8', 'feature', 'v5', 'integer'}

def allowed(text):
    # Small: a probe, not a program of its own.
    if text.count('\n') > 200 or FORBIDDEN.search(text):
        return False
    for _, module in USE_LINE.findall(text):
        if module not in PRAGMAS and not re.match(r'v?5(\.\d+)*$', module):
            return False
    return bool(re.search(r'\b(print|say|printf)\b', text))

def dedent(lines):
    width = min((len(l) - len(l.lstrip(' \t')) for l in lines if l.strip()), default=0)
    return '\n'.join(l[width:] for l in lines).strip('\n') + '\n'

def pod_blocks(path):
    """Each verbatim paragraph, and each run of them, of a pod file."""
    paragraphs = re.split(r'\n[ \t]*\n', open(path, encoding='utf-8', errors='replace').read().expandtabs(8))
    runs, run = [], []
    for p in paragraphs:
        lines = p.split('\n')
        if lines and lines[0][:1] in (' ', '\t') and lines[0].strip():
            run.append(lines)
        else:
            if run:
                runs.append(run)
            run = []
    if run:
        runs.append(run)
    for r in runs:
        for lines in r:
            yield dedent(lines)
        if len(r) > 1:
            yield dedent([l for lines in r for l in lines + ['']])

def split_args(s):
    """The arguments of a call's brackets, split at commas outside any
    bracket or quote; None for what this cannot read."""
    args, depth, cur, quote, i = [], 0, '', None, 0
    while i < len(s):
        ch = s[i]
        if quote:
            cur += ch
            if ch == '\\':
                cur += s[i + 1:i + 2]
                i += 1
            elif ch == quote:
                quote = None
        elif ch in '\'"':
            quote, cur = ch, cur + ch
        elif ch in '([{':
            depth, cur = depth + 1, cur + ch
        elif ch in ')]}':
            depth, cur = depth - 1, cur + ch
        elif ch == ',' and depth == 0:
            args.append(cur.strip())
            cur = ''
        else:
            cur += ch
        i += 1
    if quote or depth:
        return None
    args.append(cur.strip())
    return args

TEST_WORDS = re.compile(r'\b(ok|is|isnt|is_deeply|like|unlike|cmp_ok|done_testing|plan|subtest|pass|fail|diag|note|skip|todo|can_ok|isa_ok|new_ok|explain|BAIL_OUT)\b')

def rewrite(text):
    """A Test::More file as statements that print what it tests; None when
    it is not that simple."""
    out = []
    for line in text.split('\n'):
        s = line.strip()
        if re.match(r'^use (Test::More|strict|warnings)\b[^;]*;$', s) or re.match(r'^use feature [\'"]say[\'"];$', s) \
                or re.match(r'^(plan|done_testing)\b[^;]*;$', s):
            continue
        m = re.match(r'^(\s*)(is|isnt|ok|pass|fail)\s*\((.*)\);\s*(#.*)?$', line)
        if m:
            indent, word, inside = m.group(1), m.group(2), m.group(3)
            args = split_args(inside)
            if args is None or not args[0]:
                return None
            if word in ('is', 'isnt'):
                out.append(f'{indent}say {args[0]};')
            elif word == 'ok':
                out.append(f'{indent}say(({args[0]}) ? "ok" : "not ok");')
            else:
                out.append(f'{indent}say "{"ok" if word == "pass" else "not ok"}";')
            continue
        if TEST_WORDS.search(re.sub(r'#.*', '', re.sub(r'"[^"]*"|\'[^\']*\'', '', line))):
            return None
        out.append(line)
    return '\n'.join(out)

def found(perl_src, pvm, son, chalk):
    """(name, origin, text) for every candidate."""
    pods = os.path.join(perl_src, 'pod')
    for f in sorted(os.listdir(pods)):
        if not f.endswith('.pod') or re.match(r'perl5\d+delta|perldelta|perlhist', f):
            continue
        for k, text in enumerate(pod_blocks(os.path.join(pods, f)), 1):
            yield f'pod/{f[:-4]}-{k:03d}.pl', f'perl-5.42.0:pod/{f}#{k}', text
    def tree(set_, repo, origin, skip):
        for d, dirs, files in os.walk(repo):
            dirs[:] = sorted(x for x in dirs if x != '.git' and os.path.relpath(os.path.join(d, x), repo) not in skip)
            for f in sorted(files):
                if f.endswith('.pl'):
                    rel = os.path.relpath(os.path.join(d, f), repo)
                    yield f'{set_}/{rel}', f'{origin}:{rel}', open(os.path.join(d, f), encoding='utf-8', errors='replace').read()
    yield from tree('pvm-more', pvm, 'pvm', {'conformance/mdtest', 'testdata/perlonjava'})
    unit = os.path.join(pvm, 'testdata/perlonjava')
    for d, dirs, files in os.walk(unit):
        dirs.sort()
        for f in sorted(files):
            if not f.endswith('.t'):
                continue
            rel = os.path.relpath(os.path.join(d, f), unit)
            text = open(os.path.join(d, f), encoding='utf-8', errors='replace').read()
            if re.search(r'\bTest::', text):
                if not re.search(r'^use Test::More;$', text, re.M) or re.search(r'\bTest::(?!More\b)', text):
                    continue
                text = rewrite(text)
                if text is None:
                    continue
            yield f'perlonjava/{rel[:-2]}.pl', f'pvm:testdata/perlonjava/{rel}', text
    yield from tree('son-more', son, 'perl5-son', {'t/corpus/probes', 'docs/research/son-ir-audit-2026-11-19/probes'})
    yield from tree('chalk-more', chalk, 'chalk', {'t/data/audit-probes'})

def declared(text):
    """A pod's example as perl compiles it under `use v5.42;`: when perl's
    only complaint is a global it has not seen declared (the pods are
    written without strict), a `my` of each, on the line after `use
    v5.42;`; the text unchanged when perl has no complaint; None for
    anything else."""
    for _ in range(3):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'probe.pl')
            open(path, 'w', encoding='utf-8').write(text)
            try:
                r = subprocess.run([checks.PERL, '-c', 'probe.pl'], capture_output=True, timeout=10, stdin=subprocess.DEVNULL,
                                   cwd=d, env={'PATH': os.environ.get('PATH', '')}, text=True, errors='replace')
            except subprocess.TimeoutExpired:
                return None
        if r.returncode == 0:
            return text
        names = re.findall(r'^Global symbol "([$@%]\w+)" requires explicit package name', r.stderr, re.M)
        rest = [l for l in r.stderr.splitlines() if l and not l.startswith('Global symbol') and 'had compilation errors' not in l
                and not l.startswith('Execution of') and 'too many errors' not in l]
        if not names or rest or any(n[1:] in ('a', 'b', '_') for n in names):
            return None
        names = list(dict.fromkeys(names))
        text = text.replace(USE, USE + 'my (' + ', '.join(names) + ');\n', 1)
    return None

def probe(text):
    """Whether perl makes a probe of it: it runs, in silence, prints, and
    prints the same under every seed."""
    first = None
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, 'probe.pl')
        open(path, 'w', encoding='utf-8').write(text)
        for seed in checks.SEEDS:
            try:
                r = subprocess.run([checks.PERL, 'probe.pl'], capture_output=True, timeout=10, stdin=subprocess.DEVNULL, cwd=d,
                                   env={'PATH': os.environ.get('PATH', ''), 'PERL_HASH_SEED': seed})
            except subprocess.TimeoutExpired:
                return False
            if r.returncode != 0 or r.stderr or not r.stdout or len(r.stdout) > 100_000:
                return False
            if first is None:
                first = r.stdout
            elif r.stdout != first:
                return False
    return True

def main(argv):
    perl_src, pvm, son, chalk = argv
    revisions = {name: subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
                 for name, repo in (('pvm', pvm), ('perl5-son', son), ('chalk', chalk))}
    there = set()
    for d in ('run', 'by-design', 'not-perl'):
        for root, _, files in os.walk(os.path.join(HERE, d)):
            for f in files:
                there.add(hashlib.sha1(open(os.path.join(root, f), encoding='utf-8', errors='replace').read().encode()).hexdigest())
    candidates, places = {}, {}
    seen = 0
    for name, origin, text in found(perl_src, pvm, son, chalk):
        seen += 1
        if not allowed(text):
            continue
        if not re.search(r'^use v5\.42;', text, re.M):
            text = USE + text
        key = hashlib.sha1(text.encode()).hexdigest()
        if key in there:
            continue
        if key not in candidates:
            candidates[key] = (name, text)
        places.setdefault(key, []).append(origin)
    keys = list(candidates)
    pods = [k for k in keys if candidates[k][0].startswith('pod/')]
    with Pool(int(os.environ.get('JOBS', os.cpu_count() or 2))) as pool:
        fixed = pool.map(declared, [candidates[k][1] for k in pods], chunksize=20)
    for k, text in zip(pods, fixed):
        if text is None:
            del candidates[k]
            continue
        k2 = hashlib.sha1(text.encode()).hexdigest()
        if k2 != k:
            if k2 in there or k2 in candidates:
                del candidates[k]
                continue
            candidates[k2] = (candidates.pop(k)[0], text)
            places[k2] = places.pop(k)
    keys = list(candidates)
    with Pool(int(os.environ.get('JOBS', os.cpu_count() or 2))) as pool:
        kept = pool.map(probe, [candidates[k][1] for k in keys], chunksize=20)
    wrote = []
    for key, keep in zip(keys, kept):
        if not keep:
            continue
        name, text = candidates[key]
        if any(os.path.exists(os.path.join(HERE, d, name)) for d in ('run', 'by-design', 'not-perl')):
            continue
        path = os.path.join(HERE, 'run', name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w', encoding='utf-8').write(text)
        wrote.append(key)
    sources = os.path.join(HERE, 'SOURCES.tsv')
    lines = open(sources, encoding='utf-8').read().splitlines(True)
    head = [l for l in lines if l.startswith('#')]
    rows = [l for l in lines if not l.startswith('#')]
    more = ['# more: t/census/import_more.py; perl 5.42.0\'s pods are under perl\'s terms (the Artistic License or the GPL);\n',
            '# more: PerlOnJava\'s unit tests are under its licence (pvm:testdata/perlonjava/LICENSE.md, perl\'s terms); the\n',
            '# more: census\'s licence is to be settled with the repository\'s, as runtime/sort.c\'s is (D82).\n',
            '# more: perl-5.42.0 sha256 e093ef184d7f9a1b9797e2465296f55510adb6dab8842b0c3ed53329663096dc\n']
    more += [f'# more: {name} at {rev}\n' for name, rev in revisions.items()]
    head = [l for l in head if not l.startswith('# more:') and not l.startswith('# probe\t')] + more + ['# probe\tplaces\n']
    names = {l.split('\t')[0] for l in rows}
    rows += [candidates[k][0] + '\t' + ' '.join(places[k]) + '\n' for k in wrote if candidates[k][0] not in names]
    with open(sources, 'w', encoding='utf-8') as f:
        f.writelines(head + sorted(rows))
    print(f'{seen} programs read; {len(candidates)} distinct and allowed; {len(wrote)} probes written')

if __name__ == '__main__':
    main(sys.argv[1:])
