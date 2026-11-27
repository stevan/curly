#!/usr/bin/env python3
"""A reducer for what the fuzzer finds: lines taken out of a program, and
whole blocks, while its verdict stays what it was (run.py's judge).

    python3 docs/briefs/fuzz/reduce.py FILE [OUT]

FILE is a program kept by run.py (its first line, `# VERDICT: ...`, says
what to keep); OUT, by default FILE with `.min.pl`, is written as it
shrinks. A line is taken out with the block it opens, if it opens one.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run  # noqa: E402 (sets the working directory to the repository)

BUILD = 'build/fuzz-reduce'


def verdict(text, rt, knobs):
    os.makedirs(BUILD, exist_ok=True)
    path = f'{BUILD}/r{os.getpid()}.pl'
    open(path, 'w').write(text)
    built = subprocess.run(['node', 'bin/curlyc.ts', '-o', path[:-3], path], capture_output=True, text=True,
                           env=dict(os.environ, CURLY_RT_OBJ=rt))
    if built.returncode != 0:
        return 'REFUSED' if built.returncode == 1 else 'CRASH'
    env = dict(knobs, PATH=os.environ.get('PATH', ''))
    ours = run.run([path[:-3]], env, run.OURS_LIMIT)
    perl = [run.run([run.PERL, path], {'PATH': os.environ.get('PATH', ''), 'PERL_HASH_SEED': s}, run.PERL_LIMIT) for s in run.SEEDS]
    if 'runaway' in perl or ours == 'runaway':
        return 'UNJUDGED'
    perl = [p if p is None else (p[0], run.ADDR.sub(b'0xADDR', p[1]), run.ADDR.sub(b'0xADDR', p[2])) for p in perl]
    v = run.judge(perl, ours)[0]
    if v == 'WRONG' and ours is not None and ours[0] == 2:
        v = 'CRASH'
    return v


def chunks(lines, i):
    """The lines from i to the end of the block line i opens, if it does."""
    depth = 0
    for j in range(i, len(lines)):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth <= 0:
            return j + 1
    return i + 1


def main(argv):
    src = open(argv[0]).read().split('\n')
    want = src[0].split(':')[0].lstrip('# ').strip()
    out = argv[1] if len(argv) > 1 else argv[0][:-3] + '.min.pl'
    lines = src[1:]
    rt = os.path.abspath(f'{BUILD}/rt.o')
    knobs = run.checks.knobs()
    assert verdict('\n'.join(lines), rt, knobs) == want, 'the program is not ' + want
    changed = True
    while changed:
        changed = False
        i = 1  # `use v5.42;` stays
        while i < len(lines):
            for end in sorted({chunks(lines, i), i + 1}, reverse=True):
                trial = lines[:i] + lines[end:]
                if verdict('\n'.join(trial), rt, knobs) == want:
                    lines = trial
                    changed = True
                    open(out, 'w').write('\n'.join(lines))
                    break
            else:
                i += 1
    open(out, 'w').write('\n'.join(lines))
    print(f'{out}: {len(lines)} lines, still {want}')


if __name__ == '__main__':
    main(sys.argv[1:])
