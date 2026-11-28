#!/usr/bin/env python3
"""The second review of step 21a, by a reader who did not build it: each
case of a cases file run under perl 5.42 and under the compiler, both given
the same stdin, arguments and environment (PATH and the collector's knobs),
and stdout, stderr and the exit status compared apart. A verdict a case:
`same`, `fault` (the program ends with a fault), `refused` (the compiler
does not take it), or `WRONG`. A case is a program's body, or a dict with
`p` and any of `stdin`, `args`, `env`, `open` (the `use open` line).

    python3 docs/briefs/step21-review/reader/drive.py docs/briefs/step21-review/reader/cases7.py
    ... cases7.py --only N     # one case, shown
    ... cases7.py -f -r        # show the faults and the refusals too

README.md beside this directory has what it found."""
import threading, os, subprocess, sys, hashlib, importlib.util
from concurrent.futures import ThreadPoolExecutor
PERL = os.environ.get('CURLY_PERL', '/opt/perl-5.42/bin/perl')
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
WORK = os.path.join(ROOT, 'build', 'review21'); os.makedirs(WORK, exist_ok=True)
RT = os.path.join(WORK, 'rt.o')
OPEN = "use open ':std', ':encoding(UTF-8)';\n"
LOCKS = {}; DONE = {}; WL = threading.Lock()
def norm(c):
    if isinstance(c, str): c = {'p': c}
    c.setdefault('stdin', b'a\nb\nc\n'); c.setdefault('args', []); c.setdefault('env', {}); c.setdefault('open', False)
    if isinstance(c['stdin'], str): c['stdin'] = c['stdin'].encode()
    return c
def run(c):
    c = norm(c)
    src = 'use v5.42;\n' + (c.get('pre','')) + (OPEN if c['open'] else '') + c['p'] + '\n'
    h = hashlib.sha1(src.encode()).hexdigest()[:12]
    f = os.path.join(WORK, h + '.pl')
    with WL:
        if not os.path.exists(f): open(f, 'w').write(src)
    env = {'PATH': os.environ['PATH'], 'CURLY_GC_STRESS': '1', 'CURLY_GC_POISON': '1', 'CURLY_HEAP_CAP': '268435456'}; env.update(c['env'])
    def go(cmd, e):
        try:
            r = subprocess.run(cmd, input=c['stdin'], capture_output=True, env=e, timeout=30)
            return (r.stdout, r.stderr, r.returncode)
        except subprocess.TimeoutExpired:
            return (b'', b'TIMEOUT', -99)
    pe = dict(env)
    P = go([PERL, f] + c['args'], pe)
    ce = dict(os.environ); ce['CURLY_RT_OBJ'] = RT
    with LOCKS.setdefault(h, threading.Lock()):
        if h not in DONE:
            DONE[h] = subprocess.run(['node', ROOT + '/bin/curlyc.ts', '-o', os.path.join(WORK, h), f], capture_output=True, env=ce)
    r = DONE[h]
    if r.returncode != 0:
        return (c, src, 'refused' if r.returncode == 1 else 'COMPILER', P, (b'', r.stderr, r.returncode))
    ke = dict(env); ke.update(CURLY_GC_STRESS='1', CURLY_GC_POISON='1', CURLY_HEAP_CAP='268435456')
    C = go([os.path.join(WORK, h)] + c['args'], ke)
    if C[2] == 1 and C[1].rstrip().split(b'\n')[-1].startswith(b'fault:'): v = 'fault'
    elif C == P: v = 'same'
    else: v = 'WRONG'
    return (c, src, v, P, C)
def main():
    spec = importlib.util.spec_from_file_location('cases', sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    cases = m.CASES
    verbose = '-v' in sys.argv
    if '--only' in sys.argv: cases = [cases[int(sys.argv[sys.argv.index('--only')+1])]]; verbose = True
    # build the runtime once
    if not os.path.exists(RT):
        run('say 1;')
    counts = {}
    with ThreadPoolExecutor(3) as ex:
        for i, (c, src, v, P, C) in enumerate(ex.map(run, cases)):
            counts[v] = counts.get(v, 0) + 1
            if v in ('WRONG', 'COMPILER') or verbose or (v == 'fault' and '-f' in sys.argv) or (v == 'refused' and '-r' in sys.argv):
                print(f'=== {i} {v}\n{src}--- stdin {c["stdin"]!r} args {c["args"]} env {c["env"]} \n--- perl {P}\n--- curly {C}')
    print(counts)
main()
