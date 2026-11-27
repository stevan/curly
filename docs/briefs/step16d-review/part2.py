#!/usr/bin/env python3
"""The review of step 16d (D254 to D258), as a separate pass by the builder
(no second agent could be spawned in this session): three hunts, each held
to perl 5.42.

    python3 docs/briefs/step16d-review/part2.py tables     # every character's uc, lc, ucfirst, lcfirst, quotemeta
    python3 docs/briefs/step16d-review/part2.py escapes N  # N random strings of case escapes and variables
    python3 docs/briefs/step16d-review/part2.py substr N   # N random substr of four, and scalar reverse

A program the language runs to its end must print what perl prints; one it
faults must have printed the start of it. Anything else is WRONG.
"""
import concurrent.futures
import os
import random
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
PERL = os.environ.get('CURLY_PERL', 'perl')


def both(text, timeout=600):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 'p.pl')
        open(src, 'w', encoding='utf-8').write(text)
        out = os.path.join(d, 'p')
        c = subprocess.run(['node', os.path.join(ROOT, 'bin', 'curlyc.ts'), '-o', out, src], capture_output=True)
        p = subprocess.run([PERL, src], capture_output=True, timeout=timeout)
        if c.returncode != 0:
            return 'REFUSED', c.stderr.decode(errors='replace'), p.stdout
        r = subprocess.run([out], capture_output=True, timeout=timeout)
        if r.returncode == 0:
            return ('SAME' if r.stdout == p.stdout else 'WRONG'), r.stdout, p.stdout
        if r.returncode == 1 and p.stdout.startswith(r.stdout):
            return 'LOUD', r.stderr.decode(errors='replace'), p.stdout
        return 'WRONG', r.stdout + r.stderr, p.stdout + p.stderr


TABLES = r'''use v5.42;
sub hex_of($s) {
    my $out = "";
    for my $k (0 .. length($s) - 1) {
        $out .= sprintf("%X ", ord(substr($s, $k, 1)));
    }
    return $out;
}
my $c = 0x80;
while ($c <= 0x10FFFF) {
    if ($c == 0xD800) {
        $c = 0xE000;
    }
    my $s = chr($c);
    my $line = sprintf("%X", $c) . ": " . hex_of(uc($s)) . "| " . hex_of(lc($s)) . "| " . hex_of(ucfirst($s)) . "| " . hex_of(lcfirst($s)) . "| " . hex_of(quotemeta($s));
    say $line if uc($s) ne $s || lc($s) ne $s || ucfirst($s) ne $s || lcfirst($s) ne $s || quotemeta($s) ne $s;
    $c++;
}
say "done";
'''


def tables():
    verdict, got, perl = both(TABLES)
    print(verdict, len(perl.splitlines()), 'lines from perl')
    if verdict != 'SAME':
        a, b = got if isinstance(got, bytes) else got.encode(), perl
        for x, y in zip(a.splitlines(), b.splitlines()):
            if x != y:
                print('language:', x, '\nperl:    ', y)
                break


PIECES = ['a', 'B', 'x y', '.', '-', '\\U', '\\L', '\\Q', '\\E', '\\u', '\\l', '$x', '$e', '$u', '${x}d', '@a', '$a[0]', '\\x{e9}', '\\x{df}', '\\x{130}', '\\n']


def escapes(count):
    rnd = random.Random(16)
    lines = []
    for _ in range(count):
        s = ''.join(rnd.choice(PIECES) for _ in range(rnd.randrange(1, 7)))
        lines.append(s)
    progs = []
    for k in range(0, len(lines), 1):
        body = 'use v5.42;\nuse open ":std", ":encoding(UTF-8)";\nmy $x = "fOo";\nmy $e = "";\nmy $u = "\\x{e9}T\\x{df}";\nmy @a = ("pQ", "r");\nsay "[' + lines[k] + ']";\n'
        progs.append(body)
    return progs


def substrs(count):
    rnd = random.Random(42)
    progs = []
    words = ['abc', '', 'h\\x{e9}llo', '12345', 'a']
    for _ in range(count):
        st = []
        for _ in range(6):
            w = rnd.choice(words)
            o = rnd.choice(['0', '1', '-1', '2', '-3', '5', '1.5', '-0.5', '"2"'])
            n = rnd.choice(['0', '1', '-1', '2', '9', '-5', '0.5'])
            r = rnd.choice(['""', '"XY"', '"\\x{263a}"', '7'])
            st.append(f'$s = "{w}"; substr($s, {o}, {n}, {r}); say $s;')
            st.append(f'say scalar reverse("{w}", {r});')
        progs.append('use v5.42;\nuse open ":std", ":encoding(UTF-8)";\nmy $s;\n' + '\n'.join(st) + '\n')
    return progs


def hunt(progs):
    tally = {}
    with concurrent.futures.ThreadPoolExecutor(int(os.environ.get('JOBS', '2'))) as pool:
        for text, (verdict, got, perl) in zip(progs, pool.map(lambda t: both(t, 20), progs)):
            tally[verdict] = tally.get(verdict, 0) + 1
            if verdict == 'WRONG':
                print('==== WRONG\n' + text + '-- language:\n' + str(got) + '\n-- perl:\n' + str(perl))
    print(tally)


if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'tables':
        tables()
    elif what == 'escapes':
        hunt(escapes(int(sys.argv[2])))
    else:
        hunt(substrs(int(sys.argv[2])))
