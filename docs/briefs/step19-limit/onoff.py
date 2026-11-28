#!/usr/bin/env python3
"""The matcher with what D240 to D242 gave it (the memory of what it has
tried, runs, the skips of starts) held to the matcher without, which
CURLY_RE_PLAIN=1 makes of the same binary: no perl is asked. Whatever
perl says, the two must say the same, for none of the three may change an
answer.

The patterns and subjects are the independent review's
(docs/briefs/step19-review/differential.py: its grammar, its sampled and
spoiled subjects, and since D240 its long ones), every pattern the
compiler's front end takes. They are compiled in programs of forty
patterns, and those with a long subject in programs of five; each program
is run twice, and every line the two runs both print is compared. A run
that faults (`pattern match too long`, `out of memory`) prints up to its
fault, so the lines after the earlier fault of the two are not compared,
and are counted.

    python3 docs/briefs/step19-limit/onoff.py [COUNT] [SEED] [MODE]

It ends 1 if any line differs, or if a run stops in any way but a fault.
"""
import bisect, os, random, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'step19-review'))
import differential as d


def batch(tmp, k, tests):
    """One program, run both ways: (lines compared, lines lost to a fault,
    the differences, the faults of each run)."""
    text, starts = d.PRELUDE, []
    for n, written, subjects, glob in tests:
        starts.append(text.count('\n') + 1)
        text += d.block(n, written, subjects, glob)
    path = os.path.join(tmp, f'o{k}.pl')
    open(path, 'w').write(text)
    env = dict(os.environ, CURLY_RT_OBJ=os.path.join(tmp, 'rt.o'))
    c = subprocess.run(['node', os.path.join(d.ROOT, 'bin', 'curlyc.ts'), '-o', path[:-3], path], capture_output=True, env=env)
    if c.returncode != 0:
        return 0, 0, [('the compiler refused a program whose patterns it took one by one', c.stderr.decode(errors='replace')[:300], '')], [], []
    runs = []
    for plain in ('', '1'):
        try:
            r = subprocess.run([path[:-3]], capture_output=True, timeout=600, env=dict(os.environ, CURLY_RE_PLAIN=plain))
        except subprocess.TimeoutExpired:
            return 0, 0, [('a run went past ten minutes', 'plain' if plain else 'with', '')], [], []
        fault = re.search(rb'^fault: (.*) at .* line (\d+)\.$', r.stderr, re.M)
        if r.returncode != 0 and fault is None:
            return 0, 0, [('a run stopped, and not with a fault', r.stderr.decode(errors='replace')[:300], '')], [], []
        runs.append((r.stdout.decode().splitlines(), (fault.group(1).decode(), tests[bisect.bisect_right(starts, int(fault.group(2))) - 1][1]) if fault else None))
    (on, on_fault), (off, off_fault) = runs
    by = {t[0]: t[1] for t in tests}
    diffs, bad = [], set()
    for x, y in zip(on, off):
        if x != y:
            n = int(x.split(' ')[0])
            if n not in bad:
                bad.add(n)
                diffs.append((by.get(n, '?'), x[:300], y[:300]))
    if on_fault is None and off_fault is None and len(on) != len(off):
        diffs.append(('the outputs are of different lengths', str(len(on)), str(len(off))))
    whole = max(len(on), len(off))
    return min(len(on), len(off)), whole - min(len(on), len(off)), diffs, [on_fault] if on_fault else [], [off_fault] if off_fault else []


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    mode = sys.argv[3] if len(sys.argv) > 3 else 'wide'
    g = d.Gen(random.Random(seed), mode, random.Random(seed * 7919 + 1))
    seen, cases = set(), []
    while len(cases) < count:
        written, subjects = g.pattern()
        if written not in seen:
            seen.add(written)
            cases.append((written, subjects))
    ours = d.classify(['node', os.path.join(HERE, '..', 'step19-review', 'classify.ts')], [d.probe(w) for w, _ in cases])
    tests = [(n, w, s, bool(re.search(r'g[a-z]*$', w))) for n, ((w, s), o) in enumerate(zip(cases, ours)) if o == '']
    short = [t for t in tests if all(len(s) <= 60 for s in t[2])]
    long = [t for t in tests if any(len(s) > 60 for s in t[2])]
    batches = [short[k:k + 40] for k in range(0, len(short), 40)] + [long[k:k + 5] for k in range(0, len(long), 5)]
    same, lost, diffs, on_faults, off_faults = 0, 0, [], [], []
    with tempfile.TemporaryDirectory() as tmp:
        with ThreadPoolExecutor(max_workers=int(os.environ.get('JOBS', '3'))) as pool:
            for a, b, c, e, f in pool.map(lambda kb: batch(tmp, kb[0], kb[1]), enumerate(batches)):
                same += a
                lost += b
                diffs += c
                on_faults += e
                off_faults += f
    print(f'{mode}, seed {seed}: {len(cases)} patterns, {len(tests)} taken, {len(long)} of them with subjects of 300 characters or more; {len(batches)} programs')
    print(f'lines both runs printed: {same}; lines after a fault of one run, not compared: {lost}')
    for name, faults in (('with D240 to D242', on_faults), ('plain', off_faults)):
        kinds = {}
        for what, written in faults:
            kinds.setdefault(what, []).append(written)
        print(f'programs that faulted, {name}: {len(faults)}')
        for what, ws in sorted(kinds.items()):
            print(f'  {len(ws):5}  {what}    e.g. ' + ', '.join(repr(w) for w in sorted(ws, key=len)[:4]))
    print(f'DIFFERENT: {len(diffs)}')
    for written, x, y in diffs[:40]:
        print(f'  {written!r}\n    with:  {x}\n    plain: {y}')
    sys.exit(1 if diffs else 0)


if __name__ == '__main__':
    main()
