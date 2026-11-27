#!/usr/bin/env python3
"""The fuzzer broken on purpose (README.md here): three breakages of the
compiler and the runtime, each applied in turn, the fuzzer run from one
seed until it finds a WRONG (or a CRASH), and the file put back.

    python3 docs/briefs/fuzz/breakages.py [FIRST [LIMIT]]

For each breakage it prints how many programs the fuzzer took to see it.
A breakage it does not see in LIMIT programs is a hole in the generator.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))

BREAKAGES = [
    ('operand order: the right operand of an arithmetic operator worked out before the left',
     'compiler/src/codegen.ts',
     """        const left = genExpr(e.left, b);
        // `&&`, `||`, `//`: the value is the left operand, unless the test""",
     """        const right0 = op?.when === undefined ? genExpr(e.right, b) : undefined;
        const left = genExpr(e.left, b);
        // `&&`, `||`, `//`: the value is the left operand, unless the test"""),
    ('a slice off by one: the last index of a slice of an array dropped',
     'runtime/rt.c',
     """    for (uint64_t n = 0; n < ix->count; n++) {
        int64_t at = place(a->count, whole_of(cx, ix->items[n]));""",
     """    for (uint64_t n = 0; n + 1 < ix->count; n++) {
        int64_t at = place(a->count, whole_of(cx, ix->items[n]));"""),
    ('a late read made early: a variable copied where it is written, not read when its operator runs (D14)',
     'compiler/src/codegen.ts',
     """    case 'var': return { c: variable(b, e), place: true };""",
     """    case 'var': return temp(b, variable(b, e));"""),
]
# the first breakage's second half: the right operand is the one worked out before
SECOND = ("""        const right = genExpr(e.right, b);
        if (op?.rt === undefined)""", """        const right = right0!;
        if (op?.rt === undefined)""")


def main(argv):
    first = int(argv[0]) if argv else 900000
    limit = int(argv[1]) if len(argv) > 1 else 2000
    os.chdir(ROOT)
    for n, (what, path, old, new) in enumerate(BREAKAGES):
        src = open(path).read()
        assert src.count(old) == 1, f'{path}: the text to break is not there once: {old[:60]}'
        new_src = src.replace(old, new)
        if n == 0:
            assert new_src.count(SECOND[0]) == 1
            new_src = new_src.replace(*SECOND)
        out = f'build/fuzz-broken-{n}'
        subprocess.run(['rm', '-rf', out])
        try:
            open(path, 'w').write(new_src)
            subprocess.run([sys.executable, os.path.join(HERE, 'run.py'), str(first), str(limit), '--stop', '--out', out], capture_output=True, text=True)
        finally:
            open(path, 'w').write(src)
        finds = sorted(os.listdir(os.path.join(out, 'finds'))) if os.path.isdir(os.path.join(out, 'finds')) else []
        seeds = sorted(int(re.search(r'-(\d+)\.pl$', f).group(1)) for f in finds if f.startswith(('WRONG', 'CRASH')))
        if seeds:
            print(f'SEEN after {seeds[0] - first + 1} programs (seed {seeds[0]}): {what}')
        else:
            print(f'NOT SEEN in {limit} programs: {what}')
        sys.stdout.flush()


if __name__ == '__main__':
    main(sys.argv[1:])
