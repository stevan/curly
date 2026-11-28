#!/usr/bin/env python3
"""The independent review of step 19: /i at the edge of ASCII (D230).

Every pattern here is matched under /i against every subject, each pair a
program of its own, under perl and compiled. What must hold: a pattern
with a character past ASCII is refused; a subject with one is the fault
`a match without regard to case of a string with a character past ASCII`,
whatever perl answers (it folds by Unicode's tables: the Kelvin sign is a
k, the long s an s, the sharp s two); and everything else prints what perl
prints.

    python3 docs/briefs/step19-review/folds.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
PERL = os.environ.get('CURLY_PERL', 'perl')

PATTERNS = ['k', 'K', 's', 'ss', 'st', 'fi', 'i', 'I', '[a-z]', '[^k]', '[k-s]+', '\\w', '.', 'a|k', '(k)\\1', '(S)s', '[^a-z]', '[A-Z]{2}', 'ß', '\\x{df}', '[\\x{17f}]', 'ſ', '\\x{212A}', '[a-\\x{17f}]', 'µ', 'Σ']
SUBJECTS = ['k', 'K', 'kK', 'Ss', 'sS', 'ST', 'Fi', 'i', 'I', 'Z', '@[`{', 'K', 'ſ', 'ß', 'ﬆ', 'ﬁ', 'İ', 'ı', 'ké', 'Å', 'µ', 'ς']


def quoted(s):
    return '"' + ''.join(c if c.isascii() and c.isalnum() else '\\x{%x}' % ord(c) for c in s) + '"'


def main():
    counts = {'same': 0, 'fault': 0, 'refused': 0}
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, CURLY_RT_OBJ=os.path.join(tmp, 'rt.o'))
        for p in PATTERNS:
            for s in SUBJECTS:
                path = os.path.join(tmp, 'f.pl')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(f'use v5.42;\nuse utf8;\nmy $s = {quoted(s)};\nmy @l = $s =~ /{p}/i;\nsay scalar(@l), $s =~ /{p}/i ? "y" : "n", $s !~ /{p}/i ? "y" : "n";\n')
                perl = subprocess.run([PERL, path], capture_output=True, text=True)
                c = subprocess.run(['node', os.path.join(ROOT, 'bin', 'curlyc.ts'), '-o', path[:-3], path], capture_output=True, text=True, env=env)
                wide_p = any(ord(ch) > 127 for ch in p) or '\\x{' in p
                wide_s = any(ord(ch) > 127 for ch in s)
                if c.returncode != 0:
                    kind = 'refused'
                    ok = wide_p and 'under /i' in c.stderr
                else:
                    b = subprocess.run([path[:-3]], capture_output=True, text=True)
                    if b.returncode != 0:
                        kind = 'fault'
                        ok = wide_s and 'a match without regard to case of a string with a character past ASCII' in b.stderr
                    else:
                        kind = 'same'
                        ok = not wide_s and not wide_p and perl.returncode == 0 and perl.stderr == '' and perl.stdout == b.stdout
                counts[kind] += 1
                if not ok:
                    bad.append((p, s, kind, perl.stdout, c.stderr[:120]))
    print(f'{len(PATTERNS) * len(SUBJECTS)} pairs under /i: {counts["same"]} print what perl prints, {counts["fault"]} fault for a subject past ASCII, {counts["refused"]} refused for a pattern past ASCII; {len(bad)} not as they must be')
    for row in bad:
        print('  ', row)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
