#!/usr/bin/env python3
"""The independent review of step 19: where perl 5.42 itself answers a
match wrongly (T570), and whether the compiler refuses every such pattern.

perl's optimiser works out a string every match must hold and where, and
looks for it before it runs the pattern. For a counted repeat inside a
group that is repeated at least twice it works that string out wrongly
(`use re "debug"` shows `floating "bxaay"` for `/b+x(?:a{2}){2}y/`), so
`"b&aaaa" =~ /b+&(?:a{2}){2}/` is false. perl is the referee, so the
language cannot take such a pattern and match it rightly.

This draws patterns of that family (`differential.py`, mode `counts`) and
asks perl and Python's `re`, a matcher with no such shortcut, whether each
subject matches. Every pattern on which they differ is then put to the
compiler: one it takes is a hole in the refusal.

    python3 docs/briefs/step19-review/counts.py [COUNT] [SEED]
"""
import json
import os
import random
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import differential as d  # noqa: E402


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    r = random.Random(seed)
    g = d.Gen(r, 'counts')
    seen, cases = set(), []
    while len(cases) < count:
        written, subjects = g.pattern()
        body, flags = written[1:written.rindex('/')], written[written.rindex('/') + 1:]
        if body in seen or '\\1' in body and not body.startswith('('):
            continue
        try:
            py = re.compile(body, re.S if 's' in flags else 0)
        except re.error:
            continue
        seen.add(body)
        cases.append((body, flags.replace('g', ''), [s[:40] for s in subjects], py))
    text = 'use v5.42;\nno warnings;\n'
    for n, (body, flags, subjects, _) in enumerate(cases):
        text += f'say "{n} ", join("", map {{ $_ =~ /{body}/{flags} ? 1 : 0 }} ({", ".join(d.quoted(s) for s in subjects)}));\n'
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'c.pl')
        with open(path, 'w') as f:
            f.write(text)
        p = subprocess.run([d.PERL, path], capture_output=True, text=True, timeout=3000)
    if p.returncode != 0:
        sys.exit('perl stopped: ' + p.stderr[:400])
    differ = []
    pairs = 0
    for line in p.stdout.splitlines():
        n, bits = line.split(' ')
        body, flags, subjects, py = cases[int(n)]
        ours = ''.join('1' if py.search(s) else '0' for s in subjects)
        pairs += len(subjects)
        if ours != bits:
            k = [i for i in range(len(bits)) if bits[i] != ours[i]][0]
            differ.append((body, flags, subjects[k], bits[k]))
    taken = d.classify(['node', os.path.join(d.HERE, 'classify.ts')], [d.probe(f'/{b}/{f}') for b, f, _, _ in differ])
    holes = [x for x, t in zip(differ, taken) if t == '']
    print(f'counts, seed {seed}: {len(cases)} patterns, {pairs} pairs of a pattern and a subject asked of perl and of Python\'s re')
    print(f'perl answers differently: {len(differ)} patterns; of those the compiler takes: {len(holes)}')
    for body, flags, s, bit in sorted(holes, key=lambda x: len(x[0]))[:40]:
        print(f'  TAKEN  /{body}/{flags}  on {s!r}: perl says {bit}')
    if '--show' in sys.argv:
        for body, flags, s, bit in sorted(differ, key=lambda x: len(x[0]))[:60]:
            print(f'  /{body}/{flags}  on {s!r}: perl says {bit}')
    sys.exit(1 if holes else 0)


if __name__ == '__main__':
    main()
