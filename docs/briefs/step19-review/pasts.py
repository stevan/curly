#!/usr/bin/env python3
"""The independent review of step 19: does a string's past show in a match?

perl keeps a string either as bytes or as UTF-8, by what was done with it
before, and two strings that are `eq` may be kept differently. The
language's strings have no past, so a match whose answer under perl moves
with how its subject is kept is one the compiler cannot agree with: it
has to be refused or to fault. (It was found by `differential.py`, as
T569: after a lazy quantifier before a character past U+00FF, the next
quantifier perl runs is lazy too, on a subject kept as bytes.)

This asks perl alone. Each pattern the compiler takes (drawn as
`differential.py` draws them) is matched against each subject that has no
character past U+00FF twice: as written, and after `utf8::upgrade`. Any
pair of answers that differ is printed.

    python3 docs/briefs/step19-review/pasts.py [COUNT] [SEED] [MODE]
"""
import json
import os
import random
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import differential as d  # noqa: E402

HEAD = '''use v5.42;
use utf8;
use open ':std', ':encoding(UTF-8)';
no warnings;
sub enc(@l) { return scalar(@l) . ":" . join("", map { defined $_ ? "<" . join(".", map { ord } split //, $_) . ">" : "u" } @l); }
'''


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    mode = sys.argv[3] if len(sys.argv) > 3 else 'wide'
    r = random.Random(seed)
    g = d.Gen(r, mode)
    seen, cases = set(), []
    while len(cases) < count:
        written, subjects = g.pattern()
        subjects = [s for s in subjects if all(ord(c) < 256 for c in s)]
        if written in seen or not subjects:
            continue
        seen.add(written)
        cases.append((written, subjects))
    ours = d.classify(['node', os.path.join(d.HERE, 'classify.ts')], [d.probe(w) for w, _ in cases])
    perls = d.classify([d.PERL, os.path.join(d.HERE, 'classify.pl')], [d.probe(w) for w, _ in cases])
    taken = [c for c, o, p in zip(cases, ours, perls) if o == '' and p == '']
    pairs, differ = 0, []
    with tempfile.TemporaryDirectory() as tmp:
        for k in range(0, len(taken), 300):
            text = HEAD
            for n, (written, subjects) in enumerate(taken[k:k + 300]):
                text += f'for my $s ({", ".join(d.quoted(s) for s in subjects)}) {{\nmy $t = $s; utf8::upgrade($t);\nmy $x = enc($s =~ {written}); my $y = enc($t =~ {written});\nsay "{k + n} ", $x, " ", $y if $x ne $y;\n}}\n'
            path = os.path.join(tmp, 'p.pl')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
            try:
                p = subprocess.run([d.PERL, path], capture_output=True, text=True, timeout=600)
            except subprocess.TimeoutExpired:
                print(f'perl ran past ten minutes on a batch of {len(taken[k:k + 300])}: not counted')
                continue
            if p.returncode != 0:
                print('perl stopped:', p.stderr[:300])
                continue
            pairs += sum(len(s) for _, s in taken[k:k + 300])
            for line in p.stdout.splitlines():
                n = int(line.split(' ')[0])
                differ.append((taken[n][0], line))
    print(f'{mode}, seed {seed}: {len(cases)} patterns, {len(taken)} taken by the compiler and perl; {pairs} pairs of a pattern and a subject with no character past U+00FF, each matched as bytes and upgraded')
    print(f'perl answers differently by how the subject is kept: {len(differ)} lines, {len(set(w for w, _ in differ))} patterns')
    for written, line in differ[:40]:
        print(f'  {written!r}\n    {line}')
    sys.exit(1 if differ else 0)


if __name__ == '__main__':
    main()
