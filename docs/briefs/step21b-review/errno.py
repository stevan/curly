#!/usr/bin/env python3
"""Step 21b's evidence for its one claim about perl's errno (D272): among
everything the language has, only `open`, and a read that meets the end of
its input, change it (and a number that underflows, D151, which faults).

Every golden test that perl runs to its end (`same`, `warns`, `dies`) is
run again with `$! = 77;` put after its pragmas and an END block that says
what `$!` is as it ends (a `dies` test by the status it
exits with): 77 for all, but a test that reads its
stdin to the end (0), opens a file, or underflows.

    python3 docs/briefs/step21b-review/errno.py        # from the root
"""
import glob, os, re, subprocess, sys, tempfile
sys.path.insert(0, 't')
import checks

PERL = os.environ.get('CURLY_PERL', 'perl')
PRAGMA = re.compile(r'^\s*(use|no)\b.*;\s*(#.*)?$')

def marked(text):
    lines = text.split('\n')
    at = 0
    for k, line in enumerate(lines):
        if PRAGMA.match(line):
            at = k + 1
        elif line.strip() and not line.lstrip().startswith('#'):
            break
    # On the pragma's own line, so that no line number moves.
    lines[at - 1] += ' $! = 77;'
    # As the last statement (perl's own shutdown changes errno before an
    # END block runs); a test that dies or exits says it by its status.
    return '\n'.join(lines) + '\n;print STDERR "\\nERRNO=", 0+$!, "\\n";\n'

def main():
    counts, odd = {}, []
    tests = sorted(glob.glob('t/*.pl'))
    with tempfile.TemporaryDirectory() as tmp:
        for path in tests:
            hdr = checks.headers(path)
            kind = hdr.get('kind', 'same')
            if kind not in ('same', 'warns', 'dies'):
                continue
            text = open(path, encoding='utf-8').read()
            copy = os.path.join(tmp, os.path.basename(path))
            open(copy, 'w', encoding='utf-8').write(marked(text))
            env = {**checks.program_environment(hdr), 'PERL_HASH_SEED': '1'}
            r = subprocess.run([PERL, copy, *checks.words(hdr.get('args', ''))], env=env, input=checks.printf_b(hdr.get('stdin', '')),
                               capture_output=True, cwd=tmp, timeout=120)
            m = re.search(rb'\nERRNO=(\d+)\n', r.stderr)
            got = m.group(1).decode() if m else f'exit {r.returncode}'
            if got == 'exit 77' and kind == 'dies':
                got = '77'
            counts[got] = counts.get(got, 0) + 1
            # What is known to change it: a read of stdin to its end (0), an
            # open, a number that underflowed (34, ERANGE: D151 faults an
            # uncaught die after one), and `exit`, which says nothing here.
            known = '<STDIN>' in text or 'open(' in text or got == '34' or (got.startswith('exit') and 'exit' in text)
            if got != '77' and not known:
                odd.append((path, got))
    print('errno as the program ends:', ', '.join(f'{n} tests {k}' for k, n in sorted(counts.items())))
    for path, got in odd:
        print(f'{path}: {got}, and nothing known to change errno is in it')
    return 1 if odd else 0

if __name__ == '__main__':
    sys.exit(main())
