#!/usr/bin/env python3
"""Step 19's evidence beyond tests (D226 to D237): random patterns and
subjects, each match run under perl 5.42 and under the compiler, and
every difference printed.

A pattern is drawn from a grammar a little wider than the language's
subset, so that the compiler's refusals are met too. Each one is first
read by compiler/src/regex.ts itself (`refusals.ts`, beside this file),
in one Node process for the lot: a refused pattern is counted by the
first words of its message, and a sample of them is run under perl alone,
to say what perl does there (prints, warns, dies). The ones it takes are
run in programs of a few hundred matches each, under perl and compiled,
each match printed where a list is wanted (its captures, undef as `u`),
where one value is (`1` or `0`), and with `!~`; the two outputs must be
the same line for line.

    python3 docs/briefs/step19-review/patterns.py [COUNT] [SEED]

`outputs.txt` beside this file is what the run recorded in the step's
account printed.
"""

import json
import os
import random
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
PERL = os.environ.get('CURLY_PERL', 'perl')
PRELUDE = 'use v5.42;\nuse utf8;\nuse open ":std", ":encoding(UTF-8)";\n'

ALPHA = 'aab c\n1_é-'
ASCII = 'aabBc 1_-\n'


def atom(r, depth, groups):
    k = r.random()
    if k < 0.30:
        return r.choice(['a', 'b', 'c', ' ', '1', '_', '-', '\\.', '\\n', '\\x{e9}', 'B'])
    if k < 0.38:
        return '.'
    if k < 0.50:
        neg = '^' if r.random() < 0.3 else ''
        items = ''.join(r.choice(['a', 'b', 'c', 'a-c', '\\d', '\\w', '\\s', ' ', '_', '\\n', '\\x{e9}', '-']) for _ in range(r.randint(1, 3)))
        return f'[{neg}{items}]'
    if k < 0.60:
        return r.choice(['\\d', '\\w', '\\s', '\\D', '\\W', '\\S'])
    if k < 0.67:
        return r.choice(['^', '$', '\\b', '\\B', '\\A', '\\z', '\\Z'])
    if k < 0.70 and groups[0] > 0:
        return f'\\{r.randint(1, min(groups[0], 9))}'
    if depth > 0:
        cap = r.random() < 0.6
        if cap:
            groups[0] += 1
        inner = alt(r, depth - 1, groups)
        return f'({inner})' if cap else f'(?:{inner})'
    return r.choice('abc')


def quant(r):
    k = r.random()
    if k < 0.65:
        return ''
    q = r.choice(['*', '+', '?', '{2}', '{1,2}', '{0,2}', '{2,}', '{1,3}'])
    if r.random() < 0.3:
        q += '?'
    return q


def seq(r, depth, groups):
    return ''.join(atom(r, depth, groups) + quant(r) for _ in range(r.randint(1, 4)))


def alt(r, depth, groups):
    n = 1 if r.random() < 0.7 else r.randint(2, 3)
    return '|'.join(seq(r, depth, groups) for _ in range(n))


def subject(r, icase):
    pool = ASCII if icase else ALPHA
    return ''.join(r.choice(pool) for _ in range(r.randint(0, 8)))


def lit(s):
    out = ''
    for ch in s:
        out += {'\n': '\\n', '"': '\\"', '\\': '\\\\', '$': '\\$', '@': '\\@', 'é': '\\x{e9}'}.get(ch, ch)
    return '"' + out + '"'


def case(r):
    groups = [0]
    pattern = alt(r, 2, groups)
    flags = ''.join(f for f in 'imsx' if r.random() < 0.2)
    if 'x' in flags:
        pattern = pattern.replace('a', ' a ', 1)
    glob = r.random() < 0.3
    s = subject(r, 'i' in flags)
    return pattern, flags, glob, s


def statements(n, pattern, flags, glob, s):
    p = f'/{pattern}/{flags}'
    lines = [f'say "{n}L:", join("|", map {{ $_ // "u" }} ({lit(s)} =~ {p}{"g" if glob else ""})), ".";']
    if not glob:
        lines.append(f'say "{n}S:", ({lit(s)} =~ {p}) ? 1 : 0, ({lit(s)} !~ {p}) ? 1 : 0;')
    return lines


def run(argv, path):
    try:
        r = subprocess.run(argv + [path], capture_output=True, timeout=120)
        return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')
    except subprocess.TimeoutExpired:
        return None, '', 'timeout'


def compile_and_run(lines, d, name):
    src = os.path.join(d, name + '.pl')
    open(src, 'w', encoding='utf-8').write(PRELUDE + '\n'.join(lines) + '\n')
    perl = run([PERL], src)
    exe = os.path.join(d, name)
    c = subprocess.run(['node', os.path.join(ROOT, 'bin', 'curlyc.ts'), '-o', exe, src], capture_output=True, text=True)
    if c.returncode != 0:
        return perl, (c.returncode, '', c.stderr)
    return perl, run([], exe)


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 19
    r = random.Random(seed)
    cases = [case(r) for _ in range(count)]
    # Which patterns the compiler takes: regex.ts itself, in one process.
    ask = [{'body': p, 'flags': f + ('g' if g else '')} for p, f, g, s in cases]
    out = subprocess.run(['node', os.path.join(HERE, 'refusals.ts')], input=json.dumps(ask), capture_output=True, text=True, check=True).stdout
    verdicts = json.loads(out)
    taken = [c for c, v in zip(cases, verdicts) if v == '']
    refused = {}
    for c, v in zip(cases, verdicts):
        if v:
            key = v.split(':')[0][:70]
            refused.setdefault(key, []).append(c)
    print(f'{count} cases, seed {seed}: {len(taken)} taken, {count - len(taken)} refused')
    for key, cs in sorted(refused.items(), key=lambda kv: -len(kv[1])):
        print(f'  refused {len(cs):6}  {key}')
    os.environ.setdefault('CURLY_RT_OBJ', os.path.join(tempfile.gettempdir(), f'step19-rt-{os.getpid()}.o'))
    differ = 0
    with tempfile.TemporaryDirectory() as d:
        batches = [taken[k:k + 250] for k in range(0, len(taken), 250)]

        def one(k):
            lines = []
            for n, c in enumerate(batches[k]):
                lines += statements(n, *c)
            return k, compile_and_run(lines, d, f'b{k}')

        # The runtime once, before the pool.
        if batches:
            one(0)
        with ThreadPoolExecutor(max_workers=int(os.environ.get('JOBS', '2'))) as pool:
            results = list(pool.map(one, range(len(batches))))
        for k, (perl, curly) in results:
            if perl == curly:
                continue
            # A batch that differs is run a case at a time, to name the case.
            for n, c in enumerate(batches[k]):
                p1, c1 = compile_and_run(statements(n, *c), d, f'one{k}_{n}')
                if p1 != c1:
                    differ += 1
                    print(f'DIFFERS {c!r}\n  perl  {p1!r}\n  curly {c1!r}')
    print(f'{len(taken)} cases run under both: {differ} differ')
    try:
        os.remove(os.environ['CURLY_RT_OBJ'])
    except OSError:
        pass
    return 1 if differ else 0


if __name__ == '__main__':
    sys.exit(main())
