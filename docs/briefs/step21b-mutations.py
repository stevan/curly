#!/usr/bin/env python3
"""Break step 21b on purpose, one way at a time, in the runtime and in each
pass of the compiler, and see that a test goes red each time: `open`,
`close`, `<$fh>`, `eof($fh)`, `print` to a handle, `$!`, perl's errno, the
handle a message names, and the refusals (D270 to D283).

    python3 docs/briefs/step21b-mutations.py            # all of them
    python3 docs/briefs/step21b-mutations.py "errno"    # those named so
    python3 docs/briefs/step21b-mutations.py --match    # only see that each piece of text is there
    python3 docs/briefs/step21b-mutations.py --from 20 --to 40

Nothing in the tree is written: a broken runtime or compiler is a copy of
bin/, compiler/src/ and runtime/ under build/mut21b/tree/. Each breakage is
run over every test of step 21b, t/6400*.pl to t/6699*.pl, the refused ones
too, with 21a's tests of stdin (t/47*.pl, whose reading 21b rewrote) and
2656, each in a directory of its own with its files, stdin and environment
(D282), until one fails; and over the runtime's own test, runtime/tests/
file.c. A breakage of the runtime is compiled into a runtime of its own.

A record of step 21b, and not part of make test: each breakage is a piece
of the text as it was then, and one that no longer matches stops the run."""
import glob
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, 't')
import checks

FILE = 'runtime/file.c'
IO = 'runtime/io.c'
UNWIND = 'runtime/unwind.c'
RT = 'runtime/rt.c'
REF = 'runtime/ref.c'
RTH = 'runtime/rt.h'
GEN = 'compiler/src/codegen.ts'
RESOLVE = 'compiler/src/resolver.ts'
CHECK = 'compiler/src/checker.ts'
PARSE = 'compiler/src/parser.ts'
LEX = 'compiler/src/lexer.ts'
NAMES = 'compiler/src/names.ts'
MUTATIONS = [
    # ---- the runtime: handles and files
    ("a handle is no reference", RTH, " || tag == RT_TAG_CODE || tag == RT_TAG_GLOB;", " || tag == RT_TAG_CODE;"),
    ("ref of a handle is the empty string", REF, "    if (v.tag == RT_TAG_GLOB) return rt_string(&STR_GLOB);\n", ""),
    ("a handle is not marked", RT, " case RT_TAG_CODE: case RT_TAG_GLOB:\n        mark_container", " case RT_TAG_CODE:\n        mark_container"),
    ("a collection closes no file", RT, "    files_reap(cx);\n", ""),
    ("a collection closes every file", FILE, "        if (f->block == NULL || ((rt_block *)f->block - 1)->marked & REACHED) {\n            link = &f->next;\n            continue;\n        }\n", ""),
    ("the handle read last, collected, is forgotten", FILE, "            cx->last_read = f->lines != 0 ? 3 : 0;", "            cx->last_read = 0;"),
    ("open's variable may hold anything", FILE, "    if (v.tag == RT_TAG_UNDEF) return rt_handle_new(cx);\n    if (v.tag == RT_TAG_GLOB) return v;", "    if (v.tag != RT_TAG_GLOB) return rt_handle_new(cx);\n    return v;"),
    ("open of a variable that holds a handle makes a new one", FILE, "    if (v.tag == RT_TAG_GLOB) return v;\n", "    if (v.tag == RT_TAG_GLOB) return rt_handle_new(cx);\n"),
    ("a file may be open twice", FILE, "        if (open_twice(cx, name, mode, f)) rt_fault(cx, \"open of a file the program has open, one of the two for writing\");", "        (void)0;"),
    ("two readers are one too many", FILE, "        if (g->mode == FILE_WRITE || mode == FILE_WRITE) return 1;", "        return 1;"),
    ("a reader does not stop a writer", FILE, "        if (g->mode == FILE_WRITE || mode == FILE_WRITE) return 1;", "        if (g->mode == FILE_WRITE) return 1;"),
    ("a writer does not stop a reader", FILE, "        if (g->mode == FILE_WRITE || mode == FILE_WRITE) return 1;", "        if (mode == FILE_WRITE) return 1;"),
    ("no collection before the fault for a file open twice", FILE, "        // A handle nothing holds is closed by a collection, as perl closed\n        // it when it was dropped.\n        rt_collect(cx);\n", ""),
    ("the handle opened again counts against itself", FILE, "        if (g == self || g->f == NULL || g->dev != st.st_dev", "        if (g->f == NULL || g->dev != st.st_dev"),
    ("open does not close what the handle had open", FILE, "    if (file_shut(f)) rt_fault(cx, \"write to a file failed\");\n    if (open_twice", "    f->f = NULL;\n    if (open_twice"),
    ("no collection when too many files are open", FILE, "        rt_collect(cx);\n        fd = open(name, flags | O_CLOEXEC, 0666);", "        fd = -1;"),
    ("a name may hold a NUL", FILE, "    if (memchr(s->bytes, 0, s->len) != NULL) rt_fault(cx, \"a NUL in a file's name\");\n", ""),
    ("a name may hold a character past ASCII", FILE, "    if (s->len != s->chars) rt_fault(cx, \"a character past ASCII in a file's name\");\n", ""),
    ("a directory is opened", FILE, "    if (fstat(fd, &st) != 0 || !S_ISREG(st.st_mode)) {", "    if (fstat(fd, &st) != 0) {"),
    ("> does not empty the file", FILE, "O_WRONLY | O_CREAT | O_TRUNC);", "O_WRONLY | O_CREAT);"),
    (">> empties the file", FILE, "O_WRONLY | O_CREAT | O_APPEND);", "O_WRONLY | O_CREAT | O_TRUNC);"),
    ("> makes no file", FILE, "O_WRONLY | O_CREAT | O_TRUNC);", "O_WRONLY | O_TRUNC);"),
    ("an open that fails is worth 1", FILE, "        cx->open_failed = 1;\n        return rt_undef();", "        cx->open_failed = 1;\n        return rt_int(1);"),
    ("an open that works is worth true", FILE, "    f->ino = st.st_ino;\n    return rt_int(1);", "    f->ino = st.st_ino;\n    return rt_bool(1);"),
    ("close leaves the file open", FILE, "    f->lines = 0;\n    if (file_shut(f)) rt_fault(cx, \"write to a file failed\");", "    f->lines = 0;\n    fflush(f->f);"),
    ("close of a closed handle is nothing", FILE, "    if (f->f == NULL) rt_fault(cx, \"close of a file handle that is not open\");\n", "    if (f->f == NULL) return rt_int(1);\n"),
    ("close keeps the count of lines", FILE, "    f->lines = 0;\n    if (file_shut(f))", "    if (file_shut(f))"),
    ("a write that fails is not seen at close", FILE, "    int failed = ferror(f->f);\n    if (fclose(f->f) != 0) failed = 1;", "    int failed = 0;\n    fclose(f->f);"),
    ("a read of a closed handle is undef", FILE, "    if (f->f == NULL) {\n        snprintf(said, sizeof said, \"%s of a file handle that is not open\", what);\n        rt_fault(cx, said);\n    }", "    if (f->f == NULL) return NULL;"),
    ("a handle open for writing is read", FILE, "    if (f->mode != FILE_READ) {\n        snprintf(said, sizeof said, \"%s of a file handle opened for writing\", what);\n        rt_fault(cx, said);\n    }\n", ""),
    ("a write to a closed handle is nothing", FILE, "    if (f->f == NULL) rt_fault(cx, \"write to a file handle that is not open\");\n", ""),
    ("a handle open for reading is written to", FILE, "    if (f->mode != FILE_WRITE) rt_fault(cx, \"write to a file handle opened for reading\");\n", ""),
    ("a read does not make its handle the one read last", FILE, "    cx->last_read = 2;\n    cx->last_file = f->block;\n", ""),
    ("a list of lines is one line", FILE, "        rt_list_add(cx, list, line);\n    }\n}\n\nrt_value rt_eof_fh", "        rt_list_add(cx, list, line);\n        return;\n    }\n}\n\nrt_value rt_eof_fh"),
    ("eof of a handle is never true", FILE, "    return rt_bool(at_end(f->f, &f->ended));", "    at_end(f->f, &f->ended);\n    return rt_bool(0);"),
    ("the handle is looked at after the list", FILE, "rt_value rt_handle_out(rt_ctx *cx, rt_value handle) {\n    file_of(cx, handle);\n", "rt_value rt_handle_out(rt_ctx *cx, rt_value handle) {\n"),
    ("say to a handle prints no newline", FILE, "    if (newline) putc('\\n', f->f);", "    (void)newline;"),
    ("what is written to a file is not looked at", FILE, "    for (uint64_t n = 1; n < a->count; n++) emit_checked(cx, a->items[n], 0, 0);\n", ""),
    ("the handle is written to its file", FILE, "    for (uint64_t n = 1; n < a->count; n++) {\n        char buf[32];", "    for (uint64_t n = 0; n < a->count; n++) {\n        char buf[32];"),
    ("a number is written as nothing", FILE, "            int k = format_number(cx, v, buf);\n            fwrite(buf, 1, (size_t)k, f->f);", "            (void)buf;"),
    ("printf to a handle prints its format", FILE, "    rt_value made = format_from(cx, list, \"printf\", 1);", "    rt_value made = array_of(cx, list)->items[1];"),
    ("printf to a handle is not looked at", FILE, "    rt_value made = format_from(cx, list, \"printf\", 1);\n    emit_checked(cx, made, 0, 0);", "    rt_value made = format_from(cx, list, \"printf\", 1);"),
    ("$! is read whenever", FILE, "    if (!cx->open_failed || cx->underflowed) rt_fault(cx, \"$! where no open has just failed\");\n", ""),
    ("$! is read after an underflow", FILE, "    if (!cx->open_failed || cx->underflowed) rt_fault", "    if (!cx->open_failed) rt_fault"),
    # ---- the runtime: perl's errno
    ("an open that works leaves errno", FILE, "    if (!isatty(fd)) cx->perl_errno = errno;", "    (void)0;"),
    ("an open that works leaves $! to be read", FILE, "    cx->open_failed = 0;\n    f->f = fdopen", "    f->f = fdopen"),
    ("an open that fails leaves errno", FILE, "        cx->perl_errno = errno;\n        cx->open_failed = 1;", "        cx->open_failed = 1;"),
    ("an open does not undo an underflow", FILE, "    cx->underflowed = 0;\n    if (fd < 0) {", "    if (fd < 0) {"),
    ("a read that meets the end leaves errno", IO, "            cx->perl_errno = 0;\n", ""),
    ("a read that meets the end leaves $! to be read", IO, "            cx->open_failed = 0;\n", ""),
    ("the end is looked for again", IO, "            *ended = 1;\n            cx->perl_errno = 0;", "            cx->perl_errno = 0;"),
    ("eof sets errno to 0", FILE, "    return rt_bool(at_end(f->f, &f->ended));", "    int end = at_end(f->f, &f->ended);\n    if (end) cx->perl_errno = 0;\n    return rt_bool(end);"),
    ("eof does not find the end for the read after it", IO, "    if (c == EOF) {\n        *ended = 1;\n        return 1;\n    }", "    if (c == EOF) return 1;"),
    ("eof takes the character it looks at", IO, "    ungetc(c, in);\n", ""),
    ("an uncaught die exits with 255", UNWIND, "        int status = (cx->perl_errno & 255) != 0 ? cx->perl_errno & 255 : 255;", "        int status = 255;"),
    ("an uncaught die exits with errno, 0 too", UNWIND, "        int status = (cx->perl_errno & 255) != 0 ? cx->perl_errno & 255 : 255;", "        int status = cx->perl_errno;"),
    # ---- the runtime: the handle a message names
    ("a message while a file is read is written", UNWIND, "    if (!newline && cx->last_read >= 2 && file_lines(cx) != 0) {", "    if (0) {"),
    ("a message with a newline is a fault too", UNWIND, "    if (!newline && cx->last_read >= 2 && file_lines(cx) != 0) {", "    if (cx->last_read >= 2 && file_lines(cx) != 0) {"),
    ("a file that has given no line stops a message", UNWIND, "    if (!newline && cx->last_read >= 2 && file_lines(cx) != 0) {", "    if (!newline && cx->last_read >= 2) {"),
    ("stdin is named whatever was read last", UNWIND, "cx->last_read != 1 || cx->stdin_lines == 0 ? snprintf", "cx->stdin_lines == 0 ? snprintf"),
    ("a read of stdin does not make it the handle read last", IO, "rt_value rt_readline(rt_ctx *cx) {\n    cx->last_read = 1;\n    cx->last_file = NULL;\n", "rt_value rt_readline(rt_ctx *cx) {\n"),
    ("eof of stdin does not make it the handle read last", IO, "    // stdin is the handle read last from here (T682).\n    cx->last_read = 1;\n    cx->last_file = NULL;\n", ""),
    # ---- the lexer
    ("<$fh> is refused", LEX, "            if (/^\\$[A-Za-z_][A-Za-z0-9_]*$/.test(inside)) {", "            if (false) {"),
    ("<$h{fh}> is a readline of $h", LEX, "            if (/^\\$[A-Za-z_][A-Za-z0-9_]*$/.test(inside)) {", "            if (/^\\$[A-Za-z_][A-Za-z0-9_]*/.test(inside)) {"),
    ("a handle after print is a value", LEX, "        if (last?.kind === 'var' && last.handle === true) return false;\n", ""),
    ("print $x if is a handle", LEX, "'until', 'for', 'foreach', 'isa']);", "'until', 'for', 'foreach', 'isa'].filter(w => w !== 'if'));"),
    ("print $x x is a handle", LEX, "const HANDLE_NOT = new Set(['x', 'eq',", "const HANDLE_NOT = new Set(['eq',"),
    ("print $fh \\ is taken", LEX, "                    if (a === '\\\\') refuse(`${lop.text} $${name} \\\\...: perl takes", "                    if (false) refuse(`${lop.text} $${name} \\\\...: perl takes"),
    ("print($fh ...) is no handle", LEX, "                if (lopKind === 'statement' && before === tokens.length - 2 && begins) {", "                if (false) {"),
    ("print $fh ! is no handle", LEX, " || (a === '!' && b !== '=' && b !== '~')\n", "\n"),
    ("print $x != is a handle", LEX, " || (a === '!' && b !== '=' && b !== '~')\n", " || a === '!'\n"),
    ("print $fh before a heredoc is no handle", LEX, "                        || (a === '<' && b === '<' && !isBlank(src[w + 2] ?? ' ') && src[w + 2] !== '=')\n", ""),
    ("a brace after print is a hash", LEX, "            if (c === '{' && name?.kind === 'word' && NAMES.get(name.text)?.kind === 'statement') {", "            if (false) {"),
    ("$! in a string reads on into a subscript", LEX, "            if (at() === '[' || at() === '{' || (src.startsWith('->', i) && (src[i + 2] === '[' || src[i + 2] === '{'))) {", "            if (false) {"),
    ("$!{ is $! and a block", LEX, "                if (at() === '{' || at() === '[') refuse(`$!${at()} is an element", "                if (false) refuse(`$!${at()} is an element"),
    ("$! ends no value", LEX, " || NAMES.get(last.text)?.kind === 'errno'));", "));"),
    # ---- the parser
    ("open takes a mode with a layer", PARSE, "!(mode.value === '<' || mode.value === '>' || mode.value === '>>')) {", "!/^(<|>|>>)/.test(mode.value)) {"),
    ("open's mode may be worked out", PARSE, "        if (mode.kind !== 'str' || mode.pieces !== undefined || mode.bare || !", "        if (mode.kind !== 'str' || mode.bare || !"),
    ("open takes two arguments", PARSE, "        if (peek().kind === ')' ) {\n            return refuse(`open with two arguments", "        if (false) {\n            return refuse(`open with two arguments"),
    ("open takes a fourth argument", PARSE, "        if (peek().kind === ',') return refuse(`open with more than three arguments: ${shape}`, peek().pos);\n", "        while (peek().kind === ',') { next(); expression(COMMA_ROW); }\n"),
    ("the path is worked out after the handle is made", PARSE, "args: [path, { kind: 'assign', op: '=', target, value: handle, pos: target.pos }], pos: head.pos };", "args: [{ kind: 'assign', op: '=', target, value: handle, pos: target.pos }, path], pos: head.pos };"),
    ("every open reads", PARSE, "        return { kind: 'apply', name: `open ${mode.value}`, args:", "        return { kind: 'apply', name: `open <`, args:"),
    ("open of a variable makes a new handle", PARSE, "args: target.kind === 'my' ? [] : [{ kind: 'var', name: target.name, pos: target.pos }], pos: target.pos };", "args: [], pos: target.pos };"),
    ("open or anything", PARSE, "        if (opens && peek().kind === 'op' && infixOp(peek().text) && !(peek().text === 'or' && tokens[i + 1]?.kind === 'word' && tokens[i + 1]!.text === 'die')) {", "        if (false) {"),
    ("close $fh before anything", PARSE, "            if (!(ends(after) || isModifier(after) || (after.kind === 'op' && after.text === 'or'))) {", "            if (false) {"),
    ("close() is taken", PARSE, "        if (head.text === 'close' && open.kind === '(' && tokens[i + 1]!.kind === ')') refuse(", "        if (false) refuse("),
    ("eof of two", PARSE, "                if (peek().kind !== ')') return refuse('eof takes one file handle, eof($fh) (D281)', peek().pos);\n", "                while (peek().kind !== ')') next();\n"),
    ("eof($fh) is eof(STDIN)", PARSE, "                return { kind: 'apply', name: 'eof handle', args: [of], pos: t.pos };", "                return { kind: 'stdineof', pos: t.pos };"),
    ("<$fh> is <STDIN>", PARSE, "            if (t.name !== undefined) return { kind: 'readline', handle:", "            if (false) return { kind: 'readline', handle:"),
    ("print to a handle prints to stdout", PARSE, "            if (to !== undefined) return { kind: 'call', name: head.text, args: [{ kind: 'apply', name: 'print handle', args: [to], pos: to.pos }, ...args], to: true, pos: head.pos };", "            if (to !== undefined) return { kind: 'call', name: head.text, args, pos: head.pos };"),
    ("print to a handle with nothing", PARSE, "                if (ends(after) || isModifier(after)) refuse(`${head.text} to a file handle with nothing to print: perl prints $_`, after.pos);\n", ""),
    ("print $fh (...) is taken", PARSE, "                if (after.kind === '(') refuse(`${head.text} to a file handle, and then (...)", "                if (false) refuse(`${head.text} to a file handle, and then (...)"),
    ("a comma after the handle's braces", PARSE, "                if (after.kind === ',') refuse(`',' after the file handle", "                if (after.kind === ',') next();\n                if (false) refuse(`',' after the file handle"),
    ("print {STDOUT} is taken", PARSE, "                if (named.kind === 'word' && (NAMES.get(named.text)?.kind === 'handle' || NAMES.get(named.text)?.kind === 'stdin')) {", "                if (false) {"),
    ("$! in a string is the text $!", PARSE, "                : p.kind === 'errno' ? { kind: 'apply', name: '$!', args: [], pos: p.pos }\n", "                : p.kind === 'errno' ? { kind: 'str', text: '', value: '$!', pos: p.pos }\n"),
    # ---- the names
    ("> appends", NAMES, "    ['open >', { kind: 'function', min: 2, rt: ['rt_open_write'] }],", "    ['open >', { kind: 'function', min: 2, rt: ['rt_open_append'] }],"),
    (">> writes", NAMES, "    ['open >>', { kind: 'function', min: 2, rt: ['rt_open_append'] }],", "    ['open >>', { kind: 'function', min: 2, rt: ['rt_open_write'] }],"),
    ("a my in open keeps the handle it had", NAMES, "rt: ['rt_handle_new', 'rt_handle'] }],", "rt: ['rt_handle_new', 'rt_handle_new'] }],"),
    ("close takes two", NAMES, "    ['close', { kind: 'function', min: 1, rt: ['rt_close'] }],", "    ['close', { kind: 'function', min: 1, rt: ['rt_close', 'rt_close'] }],"),
    # ---- the resolver and the checker
    ("<$fh> names no variable", RESOLVE, "        case 'readline': return e.handle === undefined ? undefined : walk(e.handle, declared);\n", ""),
    ("open alone is a statement that only has a value", CHECK, "            || fileStatement(s.expr);", "            || false;"),
    ("a my in open under a modifier", CHECK, "            if (modified && opened?.kind === 'assign' && opened.target.kind === 'my') {", "            if (false) {"),
    ("a my in open stands nowhere", CHECK, "            return checkExpr(w, s.expr, true, 'scalar', true);\n        }", "            return checkExpr(w, s.expr, false, 'scalar', true);\n        }"),
    ("an open in an element's index is no read", CHECK, " || fileCall(e) || (e.kind === 'apply' && e.name === 'eof handle')\n", "\n"),
    ("printf's format after a handle is the handle", CHECK, "checkFormat(s.to ? s.args.slice(1) : s.args, 'printf', s.pos);", "checkFormat(s.args.slice(s.to ? 2 : 0), 'printf', s.pos);"),
    ("open's name may be a list", CHECK, "    if (e.kind === 'apply' && e.name.startsWith('open ') && e.name !== 'open handle' && shaped(e.args[0]!, () => false)) {", "    if (false) {"),
    ("$! is read anywhere", CHECK, "    if (isErrno(e) && !errnoRead.has(e)) {", "    if (false) {"),
    ("$! in a string is refused", CHECK, "    if (e.kind === 'interp') e.parts.filter(isErrno).forEach(x => errnoRead.add(x));\n", ""),
    ("$! on the right of = is refused", CHECK, "(e.target.kind === 'var' || e.target.kind === 'my') && isErrno(e.value)) errnoRead.add(e.value);", "(e.target.kind === 'var' || e.target.kind === 'my') && false) errnoRead.add(e.value);"),
    ("$! is read on the right of any assignment", CHECK, "(e.target.kind === 'var' || e.target.kind === 'my') && isErrno(e.value)) errnoRead.add(e.value);", "isErrno(e.value)) errnoRead.add(e.value);"),
    ("a my assigned $! is refused", CHECK, "            noteErrno(s.expr);\n            checkConcat(w, s.expr);", "            checkConcat(w, s.expr);"),
    # ---- the code generator
    ("<$fh> where one value is wanted reads stdin", GEN, "    case 'readline': return temp(b, e.handle === undefined ? 'rt_readline(cx)' : `rt_readline_fh(cx, ${genExpr(e.handle, b).c})`);", "    case 'readline': return temp(b, 'rt_readline(cx)');"),
    ("<$fh> where a list is wanted is one line", GEN, "`rt_list_add_lines_fh(cx, ${list}, ${genExpr(e.handle, b).c})`];", "`rt_list_add(cx, ${list}, rt_readline_fh(cx, ${genExpr(e.handle, b).c}))`];"),
    ("say to a handle prints", GEN, "        const rt = s.to ? `rt_${s.name}_fh${s.name === 'printf' ? '' : '_list'}`", "        const rt = s.to ? `rt_${s.name === 'say' ? 'print' : s.name}_fh${s.name === 'printf' ? '' : '_list'}`"),
    ("$! has no runtime function", GEN, "name?.kind === 'unary' || name?.kind === 'changer' || name?.kind === 'errno' ? name.rt", "name?.kind === 'unary' || name?.kind === 'changer' ? name.rt"),
]

argv = sys.argv[1:]
start, stop = 0, None
if argv[:1] == ['--from']:
    start = int(argv[1])
    argv = argv[2:]
if argv[:1] == ['--to']:
    stop = int(argv[1])
    argv = argv[2:]
only = argv
if only == ['--match']:
    for name, path, old, new in MUTATIONS:
        n = open(path).read().count(old)
        if n != 1:
            print(n, name)
    print(len(MUTATIONS), 'pieces of text looked for')
    sys.exit(0)

tests = []
for src in sorted(glob.glob('t/6[4-6][0-9][0-9]-*.pl') + glob.glob('t/47[0-9][0-9]-*.pl') + glob.glob('t/2656-*.pl')):
    tests.append((src, open(src[:-3] + '.expected', 'rb').read(), checks.headers(src)))
# The tests most likely to see a breakage first: the model's own before the
# refusals, and stdin's last.
tests.sort(key=lambda t: (not ('/64' in t[0]), '/47' in t[0], t[0]))

UNIT = [('reap', 0, b'open: 1\nafter a collection: 0\nopens to read: 1\nkept\nopen: 1\nclosed: 0\n'),
        ('twice', 1, b'opens to read: 1\nkept\nfault: open of a file the program has open, one of the two for writing at file.pl line 1.\n'),
        ('write-failed', 1, b'written\nfault: write to a file failed at file.pl line 1.\n'),
        ('last-read-lines', 1, b'open after the collection: 0\nfault: a die or a warn with no newline at its end while a file a line was read from is open at file.pl line 1.\n'),
        ('last-read-none', 0, b'open after the collection: 0\nmsg at file.pl line 1.\nwarned\n')]


def unit(tree):
    """The runtime's own test of files, against the copy's runtime."""
    os.makedirs('build/unit', exist_ok=True)
    exe = 'build/mut21b/unit-file'
    cc = os.environ.get('CURLY_CC', 'cc').split()
    built = subprocess.run([*cc, '-O0', f'-I{tree}/runtime', '-o', exe, 'runtime/tests/file.c', f'{tree}/runtime/rt.c', '-lm'], capture_output=True)
    if built.returncode:
        return ['unit (does not compile)']
    bad = []
    for which, status, output in UNIT:
        r = subprocess.run(['sh', '-c', 'exec "$0" "$1" 2>&1', exe, which], capture_output=True, env={'PATH': '/usr/bin:/bin', 'CURLY_GC_STRESS': '1', 'CURLY_GC_POISON': '1'})
        if r.returncode != status or r.stdout != output:
            bad.append('unit ' + which)
    return bad


def passes(test, driver):
    src, expected, hdr = test
    name = os.path.basename(src)[:-3]
    exe = os.path.abspath(f'build/mut21b/{name}')
    built = subprocess.run(['node', driver, '-o', exe, src], capture_output=True)
    if hdr.get('kind') == 'refused':
        return built.returncode != 0 and built.stderr + f'exit: {built.returncode}\n'.encode() == expected
    if built.returncode:
        return False
    try:
        with checks.run_dir(src, hdr) as d:
            run = checks.run_capped([exe, *checks.words(hdr.get('args', ''))], checks.program_environment(hdr), checks.printf_b(hdr.get('stdin', '')), 60, cwd=d)
    except checks.Runaway:
        return False
    if run is None:
        return False
    got = run.stdout + run.stderr + (f'exit: {run.returncode}\n'.encode() if run.returncode else b'')
    return got == expected


def golden(driver, tree, runtime, whole=False):
    """The tests that fail: the first few found, unless `whole`."""
    failed = unit(tree) if runtime else []
    if failed and not whole:
        return failed
    with ThreadPoolExecutor(int(os.environ.get('JOBS', '3'))) as pool:
        for k in range(0, len(tests), 12):
            batch = tests[k:k + 12]
            failed += [os.path.basename(t[0])[:4] for t, ok in zip(batch, pool.map(lambda t: passes(t, driver), batch)) if not ok]
            if failed and not whole:
                return failed
    return failed


def copy():
    shutil.rmtree('build/mut21b/tree', ignore_errors=True)
    for part in ('bin', 'compiler/src', 'runtime'):
        shutil.copytree(part, 'build/mut21b/tree/' + part)


os.makedirs('build/mut21b', exist_ok=True)
tree = 'build/mut21b/tree'
driver = tree + '/bin/curlyc.ts'
rt = os.path.abspath('build/mut21b/rt.o')
os.environ['CURLY_RT_OBJ'] = rt
if os.path.exists(rt):
    os.remove(rt)
if start == 0 and not only:
    copy()
    asis = golden(driver, tree, True, whole=True)
    assert asis == [], f'things as they are fail: {asis}'
    print(f'{len(tests)} tests and the runtime\'s own pass as things are', flush=True)
missed = []
for name, path, old, new in MUTATIONS[start:stop]:
    if only and not any(o in name for o in only):
        continue
    copy()
    text = open(path).read()
    assert text.count(old) == 1, (name, text.count(old))
    open(tree + '/' + path, 'w').write(text.replace(old, new))
    runtime = path.startswith('runtime/')
    if os.path.exists(rt):
        os.remove(rt)
    failed = golden(driver, tree, runtime)
    if os.path.exists(rt):
        os.remove(rt)
    if failed:
        print(f'{name}: caught ({", ".join(failed[:8])})', flush=True)
    else:
        print(f'{name}: 0   <-- NOT CAUGHT', flush=True)
        missed.append(name)
print(f'{len(missed)} not caught: {missed}')
