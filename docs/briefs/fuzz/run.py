#!/usr/bin/env python3
"""The differential fuzzer: programs from gen.py, compiled, run, and held
to perl 5.42 (README.md here).

    python3 docs/briefs/fuzz/run.py FIRST COUNT [--jobs N] [--out DIR]

Seeds FIRST to FIRST + COUNT - 1. For each: the program is generated and
asked of the compiler (front.ts, one Node process per worker); a refusal
is counted by its message, the statement it names taken out, and the
program asked again, up to REPAIRS times. A program that compiles is
linked with one prebuilt runtime, run under the knobs of t/knobs.sh, and
perl is run plain under two hash seeds; the verdict is t/census.py's
judge (WARNS, perl warning where we are silent, counts as a finding).
A fault (LOUD) is counted by its message, the statement it names taken
out, and the program run again. Every WRONG, WARNS and CRASH is kept in
DIR/finds/ with its seed, and the totals go to DIR/totals-FIRST.json.
"""
import collections
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 't'))
os.chdir(ROOT)
import gen
import census
import checks

REPAIRS = 40
LOUD_REPAIRS = 12
PERL = os.environ.get('CURLY_PERL', 'perl')
OURS_LIMIT = 20
PERL_LIMIT = 5
SEEDS = ['1', '2']
ADDR = re.compile(rb'(?<=[A-Z]\()0x[0-9a-f]+(?=\))')


def norm(msg):
    """A message with its names and numbers made general, to count by."""
    m = re.sub(r' at \S+ line \d+\.\s*$', ' at line N', msg)
    m = re.sub(r"'[^']*'", "'_'", m)
    m = re.sub(r'[$@%]\w+', 'V', m)
    m = re.sub(r'\b\d+\b', 'N', m)
    m = re.sub(r'\bfn[a-z]\b', 'F', m)
    return m[:140]


class Worker:
    def __init__(self, n, out):
        self.dir = os.path.join(out, f'w{n}')
        os.makedirs(self.dir, exist_ok=True)
        self.node = subprocess.Popen(['node', os.path.join(HERE, 'front.ts')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

    def front(self, path):
        self.node.stdin.write(path + '\n')
        self.node.stdin.flush()
        line = self.node.stdout.readline()
        if not line:
            raise RuntimeError('front.ts died')
        return json.loads(line)


def run(argv, env, limit):
    """t/checks.py's run_capped, with a limit on memory too: perl asked
    for an address's worth of a string (T351) is stopped, not let loose on
    a machine others share. 1 MB of output is a runaway here."""
    import resource, signal, tempfile
    def cap():
        resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))
        resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            r = subprocess.run(argv, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err, timeout=limit, preexec_fn=cap)
        except subprocess.TimeoutExpired:
            return None
        if r.returncode == -signal.SIGXFSZ:
            return 'runaway'
        out.seek(0)
        err.seek(0)
        return (r.returncode, out.read(), err.read())


def judge(perl, ours):
    """t/census.py's judge, and one case it does not meet: a fault after
    the program wrote to stderr, which is LOUD when what it wrote, stdout
    and stderr apart, is the start of what perl writes."""
    if ours not in (None, 'runaway') and ours[0] == 1:
        lines = ours[2].split(b'\n')
        if len(lines) >= 2 and lines[-1] == b'' and lines[-2].startswith(b'fault: ') and not ours[2].startswith(b'fault: '):
            before = b'\n'.join(lines[:-2]) + b'\n'
            p = perl[0]
            if p is not None and p[1].startswith(ours[1]) and p[2].startswith(before):
                return 'LOUD', lines[-2][7:].decode('utf-8', 'replace')
            return 'WRONG', f'it faults after writing what perl does not: {census.clip(ours[1])!r} {census.clip(ours[2])!r}'
    if None not in perl and len({p[1] for p in perl}) > 1 and ours not in (None, 'runaway') and ours[0] == 1 and ours[2].startswith(b'fault: '):
        # perl's output moves (an address used as a number, where the
        # language faulted first): what both of perl's runs print first
        common = os.path.commonprefix([p[1] for p in perl])
        if common.startswith(ours[1]):
            return 'LOUD', ours[2][7:].decode('utf-8', 'replace')
    return census.judge(perl, ours)


def one(seed, w, tally, out, knobs, rt):
    head, top = gen.generate(seed)
    path = os.path.join(w.dir, f's{seed}.pl')
    exe = path[:-3]
    found = []
    first = True
    loud_left = LOUD_REPAIRS
    for attempt in range(REPAIRS + LOUD_REPAIRS + 1):
        text, ranges = gen.render(head, top)
        with open(path, 'w') as f:
            f.write(text)
        j = w.front(path)
        if 'internal' in j:
            found.append(('CRASH', 'compiler: ' + j['internal'][:300], text))
            break
        if 'refused' in j:
            tally['refusals'][norm(j['refused'])] += 1
            if first:
                tally['refused_first'] += 1
            first = False
            if attempt >= REPAIRS or not gen.delete_at(top, ranges, j['line']):
                tally['gave_up'] += 1
                break
            continue
        tally['compiled'] += 1
        if first:
            tally['compiled_first'] += 1
        first = False
        cc = subprocess.run(['cc', '-O0', '-w', f'-I{ROOT}/runtime', '-o', exe, path + '.c', rt, '-lm'], capture_output=True, text=True)
        if cc.returncode != 0:
            found.append(('CRASH', 'cc: ' + cc.stderr[:300], text))
            break
        env = dict(knobs, PATH=os.environ.get('PATH', ''))
        ours = run([exe], env, OURS_LIMIT)
        perl = [run([PERL, path], {'PATH': os.environ.get('PATH', ''), 'PERL_HASH_SEED': s}, PERL_LIMIT) for s in SEEDS]
        # perl prints an address where the language faults (D112): the
        # address moves from run to run, and the fault comes first anyway
        perl = [p if p in (None, 'runaway') else (p[0], ADDR.sub(b'0xADDR', p[1]), ADDR.sub(b'0xADDR', p[2])) for p in perl]
        if any(p not in (None, 'runaway') and b'Out of memory' in p[2] for p in perl):
            tally['verdicts']['UNJUDGED'] += 1
            tally['unjudged']['perl runs out of memory'] += 1
            break
        if 'runaway' in perl or ours == 'runaway':
            tally['verdicts']['UNJUDGED'] += 1
            tally['unjudged']['runaway'] += 1
            break
        verdict, why = judge(perl, ours)
        if verdict == 'LOUD' and not perl[0][1].startswith(ours[1]):
            verdict = 'WRONG'
        if verdict == 'WRONG' and ours and ours[0] == 2:
            verdict = 'CRASH'
        if verdict == 'WRONG' and ours is None:
            verdict = 'CRASH'
        tally['verdicts'][verdict] += 1
        if verdict == 'UNJUDGED':
            tally['unjudged'][why] += 1
            if why.startswith("perl's output moves"):
                found.append(('UNJUDGED', why, text))
        if verdict in ('WRONG', 'WARNS', 'CRASH'):
            found.append((verdict, why, text))
            break
        if verdict == 'LOUD':
            tally['faults'][norm(why)] += 1
            m = re.search(r' at \S+ line (\d+)\.\n?$', ours[2].decode('utf-8', 'replace'))
            if loud_left > 0 and m and gen.delete_at(top, ranges, int(m.group(1))):
                loud_left -= 1
                continue
        break
    if os.environ.get('FUZZ_KEEP'):
        found.append(('KEEP', tally['verdicts'].most_common(1)[0][0] if tally['verdicts'] else '', text))
    for f in (exe, path + '.c'):
        if os.path.exists(f):
            os.unlink(f)
    for verdict, why, text in found:
        os.makedirs(os.path.join(out, 'finds'), exist_ok=True)
        name = os.path.join(out, 'finds', f'{verdict}-{seed}.pl')
        with open(name, 'w') as f:
            f.write(f'# {verdict}: {why}\n'.replace('\n', ' ')[:600] + '\n' + text)
        print(f'{verdict} seed {seed}: {why[:200]}', flush=True)
    tally['programs'] += 1


def main(argv):
    first, count = int(argv[0]), int(argv[1])
    jobs = int(argv[argv.index('--jobs') + 1]) if '--jobs' in argv else 2
    out = argv[argv.index('--out') + 1] if '--out' in argv else 'build/fuzz'
    os.makedirs(out, exist_ok=True)
    rt = os.path.abspath(os.path.join(out, f'rt-{os.getpid()}.o'))
    subprocess.run(['cc', '-O1', '-c', '-w', f'-I{ROOT}/runtime', '-o', rt, f'{ROOT}/runtime/rt.c'], check=True)
    knobs = checks.knobs()
    tally = {'programs': 0, 'compiled': 0, 'compiled_first': 0, 'refused_first': 0, 'gave_up': 0,
             'verdicts': collections.Counter(), 'unjudged': collections.Counter(), 'refusals': collections.Counter(), 'faults': collections.Counter()}
    lock = threading.Lock()
    workers = [Worker(n, out) for n in range(jobs)]
    free = list(workers)
    start = time.time()

    stop = '--stop' in argv

    def task(seed):
        if stop and (tally['verdicts']['WRONG'] or tally['verdicts']['CRASH']):
            return
        with lock:
            w = free.pop()
        try:
            one(seed, w, tally, out, knobs, rt)
        except Exception as e:
            print(f'ERROR seed {seed}: {e!r}', flush=True)
        finally:
            with lock:
                free.append(w)
            if tally['programs'] % 200 == 0:
                print(f'.. {tally["programs"]} programs, {dict(tally["verdicts"])}, {time.time() - start:.0f}s', flush=True)

    with ThreadPoolExecutor(jobs) as pool:
        list(pool.map(task, range(first, first + count)))
    os.remove(rt)
    for w in workers:
        w.node.stdin.close()
    tally['seconds'] = round(time.time() - start)
    tally['first'] = first
    tally['count'] = count
    js = {k: (dict(v.most_common()) if isinstance(v, collections.Counter) else v) for k, v in tally.items()}
    with open(os.path.join(out, f'totals-{first}.json'), 'w') as f:
        json.dump(js, f, indent=1)
    print(json.dumps({k: v for k, v in js.items() if k not in ('refusals', 'faults')}))
    print('refusals:', json.dumps(dict(collections.Counter(js['refusals']).most_common(25)), indent=1))
    print('faults:', json.dumps(dict(collections.Counter(js['faults']).most_common(15)), indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
