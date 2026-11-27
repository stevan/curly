#!/usr/bin/env python3
"""Break step 21a on purpose, one way at a time, in the runtime and in each
pass of the compiler, and see that a test goes red each time: `<STDIN>`,
`eof(STDIN)`, `@ARGV`, `%ENV`, `exit`, STDOUT and `printf` to a handle,
`chomp` of an assignment, and the refusals (D211 to D219).

    python3 docs/briefs/step21-mutations.py            # all of them
    python3 docs/briefs/step21-mutations.py "utf8"     # those named so
    python3 docs/briefs/step21-mutations.py --match    # only see that each piece of text is there

Nothing in the tree is written: a broken runtime or compiler is a copy of
bin/, compiler/src/ and runtime/ under build/mut21/tree/. Each breakage is
run over every test of step 21a, t/4700*.pl to t/4899*.pl, the refused
ones too, and 2788, 2846 and 3144, each given its stdin, arguments and
environment as t/run.sh gives them (D220). A breakage of the runtime is
compiled into a runtime of its own, which the copy's driver links.

A record of step 21a, and not part of make test: each breakage is a piece of
the text as it was then, and one that no longer matches stops the run."""
import glob
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, 't')
import checks

IO = 'runtime/io.c'
HASH = 'runtime/hash.c'
UNWIND = 'runtime/unwind.c'
GEN = 'compiler/src/codegen.ts'
RESOLVE = 'compiler/src/resolver.ts'
CHECK = 'compiler/src/checker.ts'
PARSE = 'compiler/src/parser.ts'
LEX = 'compiler/src/lexer.ts'
SHAPES = 'compiler/src/shapes.ts'
NAMES = 'compiler/src/names.ts'
MUTATIONS = [
    # ---- the runtime
    ("a line without use open is read as UTF-8", IO, "    if (!cx->out_utf8) return bytes_as_characters(cx, cx->read_buf, n);\n", ""),
    ("a byte past ASCII is one byte of the string", IO, "    const rt_str *s = str_new(cx, n + high, n, &out);", "    const rt_str *s = str_new(cx, n, n, &out);\n    high = 0;"),
    ("a line loses its newline", IO, "        if (c == '\\n') break;", "        if (c == '\\n') { n--; break; }"),
    ("a line is read to the end of the input", IO, "        if (c == '\\n') break;", "        (void)0;"),
    ("the end of the input is an empty line", IO, "    if (n == 0) return rt_undef();", "    if (n == 0 && cx->read_room == 0) return rt_undef();"),
    ("a noncharacter is UTF-8", IO, "        if ((u >= 0xFDD0 && u <= 0xFDEF) || (u & 0xFFFE) == 0xFFFE) return -1;\n", ""),
    ("U+FDD0 is no noncharacter", IO, "(u >= 0xFDD0 && u <= 0xFDEF) || ", ""),
    ("a surrogate is UTF-8", IO, "        if (u >= 0xD800 && u <= 0xDFFF) return -1;\n", ""),
    ("an overlong form is UTF-8", IO, "        if ((more == 2 && u < 0x800) || (more == 3 && u < 0x10000) || u > 0x10FFFF) return -1;", "        if (u > 0x10FFFF) return -1;"),
    ("past U+10FFFF is UTF-8", IO, "c >= 0xF0 && c <= 0xF4 ? 3", "c >= 0xF0 && c <= 0xF7 ? 3"),
    ("a character cut short is dropped", IO, "            if (k + j >= n || (b[k + j] & 0xC0) != 0x80) return -1;", "            if (k + j >= n) return chars;\n            if ((b[k + j] & 0xC0) != 0x80) return -1;"),
    ("C0 and C1 begin a character", IO, "size_t more = c >= 0xC2 &&", "size_t more = c >= 0xC0 &&"),
    ("a list of lines is one line", IO, "        rt_list_add(cx, list, line);\n    }", "        rt_list_add(cx, list, line);\n        return;\n    }"),
    ("eof is never true", IO, "    if (c == EOF) return rt_bool(1);", "    if (c == EOF) return rt_bool(0);"),
    ("eof takes the character it looks at", IO, "    ungetc(c, stdin);\n", ""),
    ("@ARGV holds the program's path", IO, "    for (int k = 1; k < cx->argc; k++) {", "    for (int k = 0; k < cx->argc; k++) {"),
    ("@ARGV is empty", IO, "        rt_list_add(cx, *argv, arg);", "        (void)arg;"),
    ("%ENV may be changed", IO, "    env->as.a->frozen |= RT_FROZEN_READONLY;", "    (void)env;"),
    ("%ENV's value is the whole entry", IO, "        rt_value value = bytes_as_characters(cx, eq + 1, strlen(eq + 1));", "        rt_value value = bytes_as_characters(cx, *e, strlen(*e));"),
    ("%ENV's names keep their equals sign", IO, "        f[0] = bytes_as_characters(cx, *e, (size_t)(eq - *e));", "        f[0] = bytes_as_characters(cx, *e, (size_t)(eq - *e) + 1);"),
    ("a read-only hash is not looked at", HASH, '    if (h->frozen & RT_FROZEN_READONLY) rt_fault(cx, "%ENV is read-only");\n', ""),
    ("exit's status is 0", IO, "    exit((int)((uint64_t)n & 255));", "    (void)n;\n    exit(0);"),
    ("exit's status is not looked at", IO, "    int64_t n = whole_number(cx, numeric(cx, status));", "    int64_t n = status.tag == RT_TAG_INT ? status.as.i : 0;"),
    ("printf STDERR writes to stdout", IO, "    fwrite(s->bytes, 1, s->len, stderr);\n    fflush(stderr);\n}", "    fwrite(s->bytes, 1, s->len, stdout);\n    fflush(stderr);\n}"),
    ("printf STDERR prints no character past ASCII's fault", IO, "    emit_checked(cx, made, 0, 0);\n", ""),
    ("no line read is counted", IO, "    cx->stdin_lines += 1;\n", ""),
    ("a die never names the handle", UNWIND, "cx->stdin_lines == 0 ? snprintf", "1 ? snprintf"),
    # ---- the lexer
    ("<STDIN> ends no value", LEX, " || last?.kind === 'readline'", ""),
    ("<STDIN> is refused", LEX, "            if (src.startsWith('<STDIN>', i)) {", "            if (false) {"),
    ("<> is a glob", LEX, "            if (inside === '') refuse(", "            if (false) refuse("),
    # ---- the parser
    ("exit takes everything", PARSE, "                value = expression(NAMED_UNARY_ROW);\n            }\n            const after = peek();", "                value = expression(AND_ROW);\n            }\n            const after = peek();"),
    ("exit with no value exits with its line", PARSE, "            if (ends(open) || isModifier(open)) return { kind: 'exit', pos: head.pos };", "            if (ends(open) || isModifier(open)) return { kind: 'exit', value: { kind: 'int', text: '1', value: 1n, pos: head.pos }, pos: head.pos };"),
    ("an operator after exit's argument is taken", PARSE, "            if (!ends(after) && !isModifier(after)) {\n                refuse(`${show(after)} after exit's", "            if (false) {\n                refuse(`${show(after)} after exit's"),
    ("eof() is eof(STDIN)", PARSE, "            if (h.kind === ')') return refuse('eof() is", "            if (h.kind === ')') return { kind: 'stdineof', pos: t.pos };\n            if (false) return refuse('eof() is"),
    ("chomp of an assignment chomps nothing", PARSE, "                return { kind: 'do', expr: { ...assigned, value: { kind: 'apply', name: head.text, args: [assigned.value], pos: head.pos } }, pos: head.pos };", "                return { kind: 'do', expr: assigned, pos: head.pos };"),
    ("a handle is the statement's own", PARSE, "args, handle: handle.text, pos: head.pos }", "args, pos: head.pos }"),
    ("a subscript after <STDIN> is taken", PARSE, "            if (after.kind === '[' || after.kind === '{' || (after.kind === 'op' && after.text === '->')) {\n                refuse(`${show(after)} after <STDIN>", "            if (false) {\n                refuse(`${show(after)} after <STDIN>"),
    # ---- the names
    ("printf STDOUT prints", NAMES, "print: 'rt_print_list', printf: 'rt_printf' }", "print: 'rt_print_list', printf: 'rt_print_list' }"),
    ("printf STDERR prints", NAMES, "printf: 'rt_printf_err' }", "printf: 'rt_print_err_list' }"),
    # ---- the resolver
    ("my @ARGV is taken", RESOLVE, "            if (e.kind === 'myarray' && ((e.name === 'ARGV' && !e.hash) || (e.name === 'ENV' && e.hash))) {", "            if (false) {"),
    ("@ARGV is not perl's", RESOLVE, "        if (name === 'ARGV') builtin(name, false);\n", ""),
    # ---- the checker
    ("while (<STDIN>) is taken", CHECK, "        if (reads === 'bare') refuse(", "        if (false) refuse("),
    ("until and the modifiers read a line", CHECK, "        if (reads !== undefined && (s.modifier || s.negate)) {", "        if (false) {"),
    ("a for's test reads a line", CHECK, "        if (s.test && readsLine(s.test) !== undefined) {", "        if (false) {"),
    ("an element assigned a line may read or call", CHECK, "        && parts(e.target).some(readsOutside)) {", "        && false) {"),
    ("a call in an element's index is no read", CHECK, "e.kind === 'readline' || e.kind === 'stdineof' || e.kind === 'invoke' || e.kind === 'callref' || parts(e).some(readsOutside)", "e.kind === 'readline' || e.kind === 'stdineof' || parts(e).some(readsOutside)"),
    ("a line read is a constant", CHECK, "    : e.kind === 'readline' || e.kind === 'stdineof' ? false\n", ""),
    # ---- shapes and the code generator
    ("<STDIN> is one value to a return", SHAPES, "    case 'readline': return true;\n", ""),
    ("<STDIN> is one value in a list", GEN, " || e.kind === 'readline'\n", "\n"),
    ("a list's <STDIN> is one line", GEN, "        b.lines.push(`rt_list_add_lines(cx, ${list});`);", "        b.lines.push(`rt_list_add(cx, ${list}, rt_readline(cx));`);"),
    ("a while's line is tested for truth", GEN, "        const defined = readsLine(s.test) === 'assigned';", "        const defined = false;"),
    ("@ARGV is not filled", GEN, "                ...(names.builtins.get(id) === 'ARGV' ? [`    rt_argv(cx, &f[${names.slots[id]}]);`] : []),\n", ""),
    ("%ENV is not filled", GEN, "                ...(names.builtins.get(id) === 'ENV' ? [`    rt_environ(cx, &f[${names.slots[id]}]);`] : []),\n", ""),
    ("the program has no arguments", GEN, "    return rt_run_args(curly_main, ${cString(file)}, argc, argv);", "    return rt_run_args(curly_main, ${cString(file)}, 0, argv);"),
    ("exit's value is not worked out", GEN, "        const whole = genWhole(s.value, s.pos.line, out, c => [`rt_exit(cx, ${c});`]);", "        const whole = genWhole(s.value, s.pos.line, out, () => ['rt_exit(cx, rt_int(0));']);"),
]

only = sys.argv[1:]
# `--from N`: begin at the Nth breakage (a run under a time limit, resumed).
start = 0
if only[:1] == ['--from']:
    start = int(only[1])
    only = only[2:]
if only == ['--match']:
    for name, path, old, new in MUTATIONS:
        n = open(path).read().count(old)
        if n != 1:
            print(n, name)
    print(len(MUTATIONS), 'pieces of text looked for')
    sys.exit(0)

tests = []
for src in sorted(glob.glob('t/4[78][0-9][0-9]-*.pl') + glob.glob('t/2788-*.pl') + glob.glob('t/2846-*.pl') + glob.glob('t/3144-*.pl')):
    hdr = checks.headers(src)
    tests.append((src, open(src[:-3] + '.expected', 'rb').read(), hdr))


def passes(test, driver):
    src, expected, hdr = test
    name = os.path.basename(src)[:-3]
    exe = f'build/mut21/{name}'
    built = subprocess.run(['node', driver, '-o', exe, src], capture_output=True)
    if hdr.get('kind') == 'refused':
        return built.returncode != 0 and built.stderr + f'exit: {built.returncode}\n'.encode() == expected
    if built.returncode:
        return False
    try:
        run = checks.run_capped([exe, *checks.words(hdr.get('args', ''))], checks.program_environment(hdr), checks.printf_b(hdr.get('stdin', '')), 20)
    except checks.Runaway:
        return False
    if run is None:
        return False
    got = run.stdout + run.stderr + (f'exit: {run.returncode}\n'.encode() if run.returncode else b'')
    return got == expected


def golden(driver):
    with ThreadPoolExecutor(3) as pool:
        return [os.path.basename(t[0])[:4] for t, ok in zip(tests, pool.map(lambda t: passes(t, driver), tests)) if not ok]


def copy():
    shutil.rmtree('build/mut21/tree', ignore_errors=True)
    for part in ('bin', 'compiler/src', 'runtime'):
        shutil.copytree(part, 'build/mut21/tree/' + part)


os.makedirs('build/mut21', exist_ok=True)
driver = 'build/mut21/tree/bin/curlyc.ts'
rt = os.path.abspath('build/mut21/rt.o')
os.environ['CURLY_RT_OBJ'] = rt
if os.path.exists(rt):
    os.remove(rt)
copy()
whole = golden(driver)
assert whole == [], f'things as they are fail: {whole}'
print(f'{len(tests)} tests pass as things are', flush=True)
missed = []
for name, path, old, new in MUTATIONS[start:]:
    if only and not any(o in name for o in only):
        continue
    copy()
    text = open(path).read()
    assert text.count(old) == 1, (name, text.count(old))
    open('build/mut21/tree/' + path, 'w').write(text.replace(old, new))
    if path.startswith('runtime/') and os.path.exists(rt):
        os.remove(rt)
    failed = golden(driver)
    if path.startswith('runtime/') and os.path.exists(rt):
        os.remove(rt)
    if failed:
        print(f'{name}: {len(failed)} ({", ".join(failed[:8])})', flush=True)
    else:
        print(f'{name}: 0   <-- NOT CAUGHT', flush=True)
        missed.append(name)
print(f'{len(missed)} of {len(MUTATIONS) if not only else "those run"} not caught: {missed}')
