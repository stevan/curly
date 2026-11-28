#!/usr/bin/env python3
"""The review of part 1 (D250 to D253), done as a separate pass by the
builder, since no second agent could be spawned in this session: random
programs over the four constructs and what they meet (arrays, hashes,
references, loops, subs, closures, the freeze), each compiled and run, and
run by perl. A program the language runs to its end must print what perl
prints; one it faults must have printed the start of what perl prints; a
refusal is counted. Anything else is WRONG, and printed.

    python3 docs/briefs/step16d-review/part1.py [COUNT] [SEED]
"""
import os
import random
import subprocess
import sys
import tempfile
import concurrent.futures

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
PERL = os.environ.get('CURLY_PERL', 'perl')

NUM = ['0', '1', '2', '-1', '-2', '1.5', '"2"', '$n', 'scalar(@a)', '$#a', '$#b', 'scalar @b', '$r->$#*', '$#{$r}', 'scalar keys %h', '$i']
ARR = ['@a', '@b', '$r->@*', '@{$r}', '$h{l}->@*']


def num(rnd):
    return rnd.choice(NUM)


def stmt(rnd, depth=0):
    k = rnd.randrange(23)
    if k == 0:
        return f'$#a = {num(rnd)};'
    if k == 1:
        return f'$#b = {num(rnd)};'
    if k == 2:
        return f'$#{{$r}} = {num(rnd)};'
    if k == 3:
        return f'$r->$#* = {num(rnd)};'
    if k == 4:
        return f'$h{{l}}->$#* = {num(rnd)};'
    if k == 5:
        return rnd.choice(['undef $n;', 'undef @a;', 'undef @b;', 'undef %h;', 'undef $a[1];', 'undef $b[$i];', 'undef $h{x};', 'undef $r->[0];', 'undef $r->@*;', 'undef @{$r};', 'undef $h{l}->[2];', 'undef($n);', 'undef $s->$*;', 'undef ${$s};'])
    if k == 6:
        return f'say scalar {rnd.choice(ARR + ["%h"])}, " ", {num(rnd)} // "u";'
    if k == 7:
        return f'say join(",", map {{ $_ // "u" }} {rnd.choice(ARR)});'
    if k == 8:
        return f'push {rnd.choice(["@a", "@b", "$r->@*"])}, {num(rnd)};'
    if k == 9 and depth < 2:
        body = ' '.join(stmt(rnd, depth + 1) for _ in range(rnd.randrange(1, 4)))
        jump = rnd.choice(['', '', ' last OUT if $i > 4;', ' next OUT if $i == 2;'])
        return f'$i = 0; do {{ $i++;{jump} {body} }} {rnd.choice(["while", "until"])} ({rnd.choice(["$i < 3", "$i >= 2", "scalar(@a) < 4", "$#b < 2", "$i < scalar @b"])});'
    if k == 10 and depth < 2:
        body = ' '.join(stmt(rnd, depth + 1) for _ in range(rnd.randrange(1, 3)))
        return f'for my $e ({rnd.choice(["0 .. $#a", "@a", "1 .. 2", "$r->@*", "@b"])}) {{ {body} }}'
    if k == 11:
        return 'say $n // "u";'
    if k == 12:
        return f'$n = {num(rnd)};'
    if k == 13:
        return f'say defined $a[{rnd.choice(["0", "2", "5", "$#a"])}] ? "d" : "u";'
    if k == 14:
        return 'say exists $h{x} ? "e" : "n";'
    if k == 15:
        return f'f({num(rnd)});'
    if k == 16:
        return 'say $c->();'
    if k == 17:
        return f'$a[{rnd.choice(["0", "3", "$#a + 1"])}] = {num(rnd)};'
    if k == 18:
        return 'say $s->$* // "u";'
    if k == 19:
        return f'{rnd.choice(["$#a", "$#b"])} = {num(rnd)} if {rnd.choice(["$i", "!$i", "scalar @a"])};'
    if k == 20:
        return f'undef {rnd.choice(["$n", "@a", "$a[0]", "%h"])} unless {rnd.choice(["$i", "!$i"])};'
    if k == 21:
        # Items 5 to 7 (D260 to D262), asked for after the first runs.
        return rnd.choice([
            f'$n or last;', f'$i and next OUT;', f'my $q{rnd.randrange(99)} = $a[{rnd.choice(["0", "5"])}] or next;',
            f'scalar(@a) < {rnd.choice(["3", "9"])} or die "big\\n";', f'$a[0] and say "first";' if False else 'say join(",", sort(@a));',
            f'say join(",", sort({{ $b <=> $a }} @b));', f'$n > 1 and die sprintf("n %d\\n", $n);', f'f(1) or die "f" . "\\n";',
            f'say "x" . f(0) or die "never\\n";'])
    return f'say scalar @a == {rnd.choice(["0", "1", "3"])} ? "t" : "f";'


PRELUDE = '''use v5.42;
no warnings 'recursion';
my @a = (1, 2, 3);
my @b = (4);
my %h = (x => 1, l => [7, 8]);
my $r = [5, 6];
my $n = 2;
my $i = 0;
my $s = \\$n;
my $c = sub { scalar @a };
sub f($k) {
    $#b = $k;
    return scalar @b;
}
'''


def program(rnd):
    body = '\n'.join(stmt(rnd) for _ in range(rnd.randrange(3, 9)))
    return PRELUDE + 'OUT: for my $o (1) {\n' + body + '\n}\nsay "end";\n'


def run(text):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 'p.pl')
        open(src, 'w').write(text)
        out = os.path.join(d, 'p')
        env = dict(os.environ)
        c = subprocess.run(['node', os.path.join(ROOT, 'bin', 'curlyc.ts'), '-o', out, src], capture_output=True, text=True, env=env)
        try:
            p = subprocess.run([PERL, src], capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            p = None
        if c.returncode == 1:
            return ('REFUSED', text, c.stderr, '')
        if c.returncode != 0:
            return ('COMPILER', text, c.stderr, '')
        try:
            r = subprocess.run([out], capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            # Both run for ever (a do { } while whose test never fails): no
            # difference a test could see.
            return ('BOTH-HANG' if p is None else 'HANGS', text, '', '' if p is None else p.stdout)
        if p is None:
            return ('LOUD' if r.returncode == 1 else 'PERL-HANGS', text, r.stdout + r.stderr, '')
        if r.returncode == 0 or r.returncode == 255:
            same = r.stdout == p.stdout and r.returncode == p.returncode and (r.returncode == 0 or r.stderr == p.stderr)
            return ('SAME' if same else 'WRONG', text, r.stdout + r.stderr, p.stdout + p.stderr)
        if r.returncode == 1 and r.stderr.startswith('fault:') and p.stdout.startswith(r.stdout):
            return ('LOUD', text, r.stderr, '')
        return ('WRONG', text, r.stdout + r.stderr, p.stdout + p.stderr)


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    rnd = random.Random(seed)
    texts = [program(rnd) for _ in range(count)]
    tally = {}
    reasons = {}
    with concurrent.futures.ThreadPoolExecutor(int(os.environ.get('JOBS', '2'))) as pool:
        for verdict, text, got, perl in pool.map(run, texts):
            tally[verdict] = tally.get(verdict, 0) + 1
            if verdict == 'REFUSED':
                why = got.split(': ', 1)[-1].strip()[:70]
                reasons[why] = reasons.get(why, 0) + 1
            if verdict in ('WRONG', 'COMPILER', 'HANGS', 'PERL-HANGS'):
                print(f'==== {verdict}\n{text}\n-- language:\n{got}\n-- perl:\n{perl}')
    print(tally)
    for why, k in sorted(reasons.items(), key=lambda x: -x[1])[:12]:
        print(f'  {k:4} {why}')


if __name__ == '__main__':
    main()
