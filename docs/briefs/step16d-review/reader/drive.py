#!/usr/bin/env python3
"""The independent reader's differential driver for step 16d and the
census's loosenings (D250 to D262).

A case file is a Python module beside this one with `cases()`, which
yields (name, program). A program is given `use v5.42;` and the two
encoding pragmas on one line in front (so its own lines keep their
numbers plus one) unless it begins `#raw`, when it is taken as it is,
that first line dropped.

Each program is compiled, run with the tests' knobs, and run by perl, all
from one path, so a message's file name is the same. The verdicts:

    REFUSED   the compiler says no (exit 1, no binary)
    NOTPERL   perl itself does not compile it, and the compiler refuses
    SAME      stdout, stderr and the exit status are perl's
    LOUD      the program faults, having printed a prefix of what perl prints
    WRONG     anything else: it ran and differs, a fault after printing
              what perl does not, or a program the compiler takes that
              perl does not compile
    HANG      perl or the program ran out of time (looked at by hand)

    python3 docs/briefs/step16d-review/reader/drive.py FILE... [-j N] [-v]

It prints every WRONG whole, and a line of counts.
"""
import concurrent.futures
import importlib.util
import os
import resource
import subprocess
import sys
import tempfile

# CURLY_ROOT: a copy of the tree to drive, so that a long run is not
# disturbed by work in this one.
ROOT = os.environ.get('CURLY_ROOT') or os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
PERL = os.environ.get('CURLY_PERL', 'perl')
HEAD = "use v5.42; use utf8; use open ':std', ':encoding(UTF-8)';\n"
KNOBS = {'CURLY_GC_STRESS': '1', 'CURLY_GC_POISON': '1', 'CURLY_HEAP_CAP': '268435456'}


def limit():
    # T131: a program that only a fault would stop prints for ever under perl.
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))


def run(cmd, env=None, timeout=20):
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            p = subprocess.run(cmd, stdout=out, stderr=err, stdin=subprocess.DEVNULL, timeout=timeout, env=env, preexec_fn=limit)
        except subprocess.TimeoutExpired:
            return None, b'', b''
        out.seek(0)
        err.seek(0)
        code = p.returncode
        if code == -25:
            code = None
        return code, out.read(), err.read()


def judge(work, name, program):
    if program.startswith('#raw\n'):
        text = program[5:]
    else:
        text = HEAD + program
    path = os.path.join(work, name + '.pl')
    out = os.path.join(work, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    env = dict(os.environ)
    env.update(KNOBS)
    pc, po, pe = run([PERL, path], timeout=20)
    cc, _, ce = run(['node', os.path.join(ROOT, 'bin', 'curlyc.ts'), '-o', out, path], env=env, timeout=120)
    if cc is None:
        return 'HANG', text, 'the compiler ran out of time'
    if cc == 2:
        return 'WRONG', text, 'the compiler stopped (exit 2):\n' + ce.decode('utf-8', 'replace')
    perl_compiles = not (pc == 255 and (b'syntax error' in pe or b'Execution of' in pe or b'BEGIN not safe' in pe or b"Can't find string terminator" in pe or b'had compilation errors' in pe))
    if cc == 1:
        return ('REFUSED' if perl_compiles else 'NOTPERL'), text, ce.decode('utf-8', 'replace')
    rc, ro, re_ = run([out], env=env, timeout=30)
    for ext in ('', '.c'):
        try:
            os.remove(out + ext)
        except OSError:
            pass
    detail = ('--- perl (exit %s)\n%s%s--- curly (exit %s)\n%s%s' % (
        pc, po.decode('utf-8', 'replace'), pe.decode('utf-8', 'replace'),
        rc, ro.decode('utf-8', 'replace'), re_.decode('utf-8', 'replace')))
    if pc is None or rc is None:
        return 'HANG', text, detail
    if (rc, ro, re_) == (pc, po, pe):
        return 'SAME', text, ''
    if rc == 1 and re_.startswith(b'fault: ') and po.startswith(ro):
        return 'LOUD', text, detail
    return 'WRONG', text, detail


def load(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.cases())


def main():
    args = sys.argv[1:]
    jobs = 2
    verbose = False
    files = []
    only = None
    while args:
        a = args.pop(0)
        if a == '-j':
            jobs = int(args.pop(0))
        elif a == '-v':
            verbose = True
        elif a == '-k':
            only = args.pop(0)
        else:
            files.append(a)
    todo = []
    for f in files:
        stem = os.path.basename(f)[:-3]
        for name, program in load(f):
            if only is None or only in name:
                todo.append((stem + '-' + name, program))
    seen = set()
    for name, _ in todo:
        assert name not in seen, 'a name twice: ' + name
        seen.add(name)
    counts = {}
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='review16d-') as work:
        rt = os.path.join(work, 'rt.o')
        os.environ['CURLY_RT_OBJ'] = rt
        judge(work, 'warm', 'say 1;\n')
        with concurrent.futures.ThreadPoolExecutor(jobs) as pool:
            futures = [(name, pool.submit(judge, work, name, program)) for name, program in todo]
            for name, fut in futures:
                verdict, text, detail = fut.result()
                counts[verdict] = counts.get(verdict, 0) + 1
                if verdict in ('WRONG', 'HANG') or verbose:
                    print('=' * 8, verdict, name)
                    if verdict in ('WRONG', 'HANG') or verbose:
                        print(text.rstrip('\n'))
                        print(detail.rstrip('\n')[:3000])
                    sys.stdout.flush()
    print(len(todo), 'programs:', ', '.join('%d %s' % (counts[k], k) for k in sorted(counts)))
    return 1 if counts.get('WRONG') or counts.get('HANG') else 0


if __name__ == '__main__':
    sys.exit(main())
