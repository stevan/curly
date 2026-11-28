#!/usr/bin/env python3
"""The independent review of step 21b: every case of a cases file under perl
5.42 and under the compiler (both.py), and a verdict a case: `same`,
`fault` (the program ends with a fault, having written to stdout nothing
perl did not), `refused`, or `WRONG`; `FAULT-AFTER-DIFFERENCE` is a fault
after stdout that perl does not have. A case is a program's body, or a dict
with `p` and any of `stdin`, `files`, `env`, `pre` (what stands before the
body, `use v5.42;` by default).

    python3 docs/briefs/step21b-review/reader/drive.py docs/briefs/step21b-review/reader/cases7.py
    ... cases7.py --only N     # one case, shown
    ... cases7.py -f -r        # show the faults and the refusals too
    ... cases7.py --nostress   # without a collection at every allocation

cases5.py takes SEEDS=LO-HI and cases6.py PART=short or long from the
environment. INDEPENDENT.md beside this directory has what was found."""
import sys, os, importlib.util
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from both import both
def one(c):
    if isinstance(c, str): c = {'p': c}
    return c, both(c['p'], stdin=c.get('stdin', b''), files=c.get('files'), env=c.get('env'), pre=c.get('pre', 'use v5.42;\n'), stress='--nostress' not in sys.argv)
def main():
    spec = importlib.util.spec_from_file_location('cases', sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    cases = list(m.CASES)
    v_ = '-v' in sys.argv
    if '--only' in sys.argv: cases = [cases[int(sys.argv[sys.argv.index('--only') + 1])]]; v_ = True
    both('say 1;')
    counts = {}; faults = {}
    with ThreadPoolExecutor(int(os.environ.get('JOBS', '3'))) as ex:
        for i, (c, (v, P, C, src)) in enumerate(ex.map(one, cases)):
            counts[v] = counts.get(v, 0) + 1
            if v == 'fault':
                k = C[2].decode('utf-8', 'replace').split('fault: ')[-1].split(' at /')[0]; faults[k] = faults.get(k, 0) + 1
                # a fault after writing what perl does not write is a finding too
                if not (P[0] != 'TIMEOUT' and P[1].startswith(C[1])): v = 'FAULT-AFTER-DIFFERENCE'; counts[v] = counts.get(v, 0) + 1
            if v in ('WRONG', 'COMPILER', 'FAULT-AFTER-DIFFERENCE') or v_ or (v == 'fault' and '-f' in sys.argv) or (v == 'refused' and '-r' in sys.argv):
                print(f'=== {i} {v}\n{src}--- stdin {c.get("stdin", b"")!r}')
                if v == 'refused': print('--- perl', P[:3], '\n--- curly', C[1].decode().split('p.pl:')[-1].strip())
                elif v == 'fault': print('--- perl', P[:3], '\n--- curly', C[:3])
                else: print('--- perl ', P, '\n--- curly', C)
    print(counts); print(faults)
main()
