#!/usr/bin/env python3
"""Step 19's matcher on long strings (T568; D240 to D244): the time and the
most memory of one match, by the length of its subject, under the compiler
of this tree, under another tree's (the one before D240, to see what
changed), and under perl.

    python3 docs/briefs/step19-limit/measure.py                 # this tree, default knobs
    python3 docs/briefs/step19-limit/measure.py --knobs         # the knobs of t/knobs.sh
    python3 docs/briefs/step19-limit/measure.py --plain         # CURLY_RE_PLAIN=1
    python3 docs/briefs/step19-limit/measure.py --tree DIR      # bin/curlyc.ts of DIR
    python3 docs/briefs/step19-limit/measure.py --perl          # perl

Each program builds its subject with `x`, one allocation, and prints a
count. Time is the wall's, memory the most resident (wait4's, from a launcher
in C), so both carry
the program's start and the subject itself: read them against
the row called `nothing`, which builds the same subject and matches
nothing. A run cut at 120 seconds says so. A record, not a test."""
import subprocess, sys, os, tempfile, time

SIZES = [10_000, 100_000, 1_000_000, 10_000_000]
# name, the subject by its length n, the statement that prints
CASES = [
    ('nothing',   lambda n: f'"x" x {n}',                         'say length($s);'),
    ('/x+y/',     lambda n: f'"x" x {n}',                         'say $s =~ /x+y/ ? 1 : 0;'),
    ('/\\s+$/',   lambda n: f'(" " x {n - 1}) . "x"',             'say $s =~ /\\s+$/ ? 1 : 0;'),
    ('/.*b/',     lambda n: f'"a" x {n}',                         'say $s =~ /.*b/ ? 1 : 0;'),
    ('/^a*$/',    lambda n: f'"a" x {n}',                         'say $s =~ /^a*$/ ? 1 : 0;'),
    ('/needle/',  lambda n: f'("hay " x {n // 4 - 2}) . "needle"', 'say $s =~ /needle/ ? 1 : 0;'),
    ('/(\\w+)/g short', lambda n: f'"word " x {n // 5}',          'my @l = ($s =~ /(\\w+)/g); say scalar(@l);'),
    ('/(\\w+)/g long',  lambda n: f'(("w" x 999) . " ") x {n // 1000}', 'my @l = ($s =~ /(\\w+)/g); say scalar(@l);'),
    ('/(?:a|b)*c/', lambda n: f'"ab" x {n // 2}',                 'say $s =~ /(?:a|b)*c/ ? 1 : 0;'),
    ('/(a+)+b/',  lambda n: f'"a" x {n}',                         'say $s =~ /(a+)+b/ ? 1 : 0;'),
    # (T574: perl tries the group from every start, and is cut.)
    ('/((?: hay)+)$/', lambda n: f'("hay " x {n // 4}) . "needle" . (" hay" x 10)', 'my ($t) = $s =~ /((?: hay)+)$/; say length($t);'),
    ('/(\\w)\\1/',    lambda n: f'"ab" x {n // 2}',                 'say $s =~ /(\\w)\\1/ ? 1 : 0;'),
]

# A launcher in C: a child forked from Python begins with Python's own
# resident memory as its most, some 13 MB, and one forked from this does not.
LAUNCHER = r"""
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <sys/time.h>
int main(int argc, char **argv) {
    struct timeval a, b;
    gettimeofday(&a, NULL);
    pid_t child = fork();
    if (child == 0) { alarm(120); execv(argv[1], argv + 1); _exit(127); }
    int status;
    struct rusage use;
    wait4(child, &status, 0, &use);
    gettimeofday(&b, NULL);
    fprintf(stderr, "\nMEASURED %d %.2f %.1f\n", WIFSIGNALED(status) ? WTERMSIG(status) : 0,
            (b.tv_sec - a.tv_sec) + (b.tv_usec - a.tv_usec) / 1e6, use.ru_maxrss / 1024.0);
    (void)argc;
    return 0;
}
"""

def run(cmd, env, d):
    """The output, the seconds and the most resident megabytes of one run."""
    launcher = os.path.join(d, 'launch')
    open(launcher + '.c', 'w').write(LAUNCHER)
    subprocess.run([os.environ.get('CURLY_CC', 'cc'), '-O1', '-o', launcher, launcher + '.c'], check=True)
    r = subprocess.run([launcher, *cmd], env=env, capture_output=True, text=True)
    text, _, measured = (r.stdout + r.stderr).rpartition('\nMEASURED ')
    signal, took, rss = measured.split()
    text = text.strip().replace('\n', ' ')
    if signal != '0': text = 'cut at 120 s' if signal == '14' else f'signal {signal}'
    if 'fault:' in text: text = text[text.index('fault:'):text.index(' at ')]
    return text, float(took), float(rss)

def main():
    args = sys.argv[1:]
    env = dict(os.environ)
    for k in ('CURLY_GC_STRESS', 'CURLY_GC_POISON', 'CURLY_HEAP_CAP', 'CURLY_RE_PLAIN'): env.pop(k, None)
    if '--knobs' in args:
        for line in open('t/knobs.sh'):
            if line.startswith(': "${'):
                k, v = line[5:line.index('}')].split('=')
                env[k] = v
    if '--plain' in args: env['CURLY_RE_PLAIN'] = '1'
    tree = args[args.index('--tree') + 1] if '--tree' in args else '.'
    perl = '--perl' in args
    if '--one' in args:
        # One case at one size, in this process, so that the most resident
        # memory of its children is that run's alone.
        name, n = args[args.index('--one') + 1], int(args[args.index('--one') + 2])
        subject, say = next((s, p) for c, s, p in CASES if c == name)
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, 'm.pl')
            open(src, 'w').write(f'use v5.42;\nmy $s = {subject(n)};\n{say}\n')
            if perl:
                import shutil
                cmd = [shutil.which(os.environ.get('CURLY_PERL', 'perl')), src]
            else:
                c = subprocess.run(['node', os.path.join(tree, 'bin/curlyc.ts'), '-o', os.path.join(d, 'm'), src], capture_output=True, text=True)
                if c.returncode != 0:
                    print(f'{name:18} {n:>10}  refused: {c.stderr.strip()[-80:]}')
                    return
                cmd = [os.path.join(d, 'm')]
            out, took, rss = run(cmd, env, d)
            print(f'{name:18} {n:>10}  {took:7.2f} s  {rss:7.1f} MB  {out}', flush=True)
        return
    print(' '.join(a for a in args) or 'this tree, default knobs')
    for name, _, _ in CASES:
        for n in SIZES:
            subprocess.run([sys.executable, __file__, *args, '--one', name, str(n)], env=os.environ)

main()
