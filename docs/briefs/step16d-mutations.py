#!/usr/bin/env python3
"""Break step 16d, and what the census's reading asked for, on purpose, one
way at a time, in the runtime and in each pass of the compiler, and see that
a test goes red each time (D250 to D262).

    python3 docs/briefs/step16d-mutations.py            # all of them
    python3 docs/briefs/step16d-mutations.py "case"     # those named so
    python3 docs/briefs/step16d-mutations.py --match    # only see that each piece of text is there

Nothing in the tree is written: a broken runtime or compiler is a copy of
bin/, compiler/src/ and runtime/ under build/mut/tree/. Each breakage is run
against every test of this branch, t/6000*.pl to t/6299*.pl, the refused
ones too, and the older tests it moved, with the knobs of t/knobs.sh, as
t/run.sh runs them. The runtime gained no unit test of its own: the golden
tests are the whole of the net.

A record of step 16d, and not part of make test: each breakage is a piece of
the text as it was then, and one that no longer matches stops the run."""
import subprocess, glob, sys, os, shutil, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, 't')
import checks

RT = 'runtime/rt.c'
MORE = 'runtime/more16d.c'
HDR = 'runtime/rt.h'
GEN = 'compiler/src/codegen.ts'
RESOLVE = 'compiler/src/resolver.ts'
CHECK = 'compiler/src/checker.ts'
PARSE = 'compiler/src/parser.ts'
LEX = 'compiler/src/lexer.ts'
SHAPES = 'compiler/src/shapes.ts'
NAMES = 'compiler/src/names.ts'
MUTATIONS = [
 # ---- the runtime
 ("$#a below -1 is no fault", MORE, '    if (i < -1) rt_fault(cx, "an array\'s last index set below -1");\n', ''),
 ("$#a = N does not check the freeze", MORE, "    rt_array *a = changing(cx, array);\n    uint64_t count = (uint64_t)(i + 1);", "    rt_array *a = array_of(cx, array);\n    uint64_t count = (uint64_t)(i + 1);"),
 ("$#a = N grows with zeros", MORE, "    while (a->count < count) a->items[a->count++] = rt_undef();\n}", "    while (a->count < count) a->items[a->count++] = rt_int(0);\n}"),
 ("$#a = N is one short", MORE, "    uint64_t count = (uint64_t)(i + 1);", "    uint64_t count = (uint64_t)(i < 0 ? 0 : i);"),
 ("no character past ASCII is in a table", MORE, "        if (t[mid].from == c) return &t[mid];", "        if (t[mid].from == c) return NULL;"),
 ("uc is lc's table", MORE, "    const rt_case *t = which == CASE_UC ? case_uc :", "    const rt_case *t = which == CASE_UC ? case_lc :"),
 ("ucfirst is uc's table", MORE, "which == CASE_LC ? case_lc : which == CASE_UCFIRST ? case_ucfirst : case_lcfirst;", "which == CASE_LC ? case_lc : which == CASE_UCFIRST ? case_uc : case_lcfirst;"),
 ("lcfirst changes every character", MORE, "    int first = which == CASE_UCFIRST || which == CASE_LCFIRST;", "    int first = which == CASE_UCFIRST;"),
 ("uc of two U+0345 is no fault", MORE, '        if (which == CASE_UC && c == 0x345 && before == 0x345) rt_fault(cx, "uc of two U+0345 together: perl makes them one character");\n', ''),
 ("uc leaves the ASCII letters", MORE, "c >= 'a' && c <= 'z') out[0] = c - 'a' + 'A';", "c >= 'a' && c <= 'z') out[0] = c;"),
 ("a mapping is one character always", MORE, "            count = row->count;", "            count = 1;"),
 ("quotemeta quotes _", MORE, "(c >= '0' && c <= '9') || c == '_');", "(c >= '0' && c <= '9'));"),
 ("quotemeta quotes nothing past ASCII", MORE, "        else return 1;\n    }\n    return 0;", "        else return 0;\n    }\n    return 0;"),
 ("substr of four is never outside before the start", MORE, '    if (start > size || (start < 0 && end < 0)) rt_fault(cx, "substr outside of string");\n    if (start < 0) start = 0;\n    if (end > size) end = size;\n    if (end < start) end = start;\n    uint64_t from = offset_of(s, (uint64_t)start);\n    uint64_t to = offset_of(s, (uint64_t)end);\n    uint64_t len', '    if (start > size) rt_fault(cx, "substr outside of string");\n    if (start < 0) start = 0;\n    if (end > size) end = size;\n    if (end < start) end = start;\n    uint64_t from = offset_of(s, (uint64_t)start);\n    uint64_t to = offset_of(s, (uint64_t)end);\n    uint64_t len'),
 ("substr of four takes a negative length as positive", MORE, "    if (n < 0) end = size + n;\n    if (start > size || (start < 0 && end < 0)) rt_fault(cx, \"substr outside of string\");\n    if (start < 0) start = 0;\n    if (end > size) end = size;\n    if (end < start) end = start;\n    uint64_t from = offset_of(s, (uint64_t)start);\n    uint64_t to = offset_of(s, (uint64_t)end);\n    uint64_t len", "    if (n < 0) end = start - n;\n    if (start > size || (start < 0 && end < 0)) rt_fault(cx, \"substr outside of string\");\n    if (start < 0) start = 0;\n    if (end > size) end = size;\n    if (end < start) end = start;\n    uint64_t from = offset_of(s, (uint64_t)start);\n    uint64_t to = offset_of(s, (uint64_t)end);\n    uint64_t len"),
 ("substr of four keeps the piece", MORE, "    memcpy(bytes + from + r->len, s->bytes + to, s->len - to);", "    memcpy(bytes + from + r->len, s->bytes + from, s->len - to);"),
 ("scalar reverse does not reverse", MORE, "        memcpy(bytes + to, s->bytes + at, (size_t)size);", "        memcpy(bytes + at, s->bytes + at, (size_t)size);"),
 ("scalar reverse of nothing is no fault", MORE, '    if (array_of(cx, list)->count == 0) rt_fault(cx, "scalar reverse of an empty list: perl reverses $_");', '    (void)array_of(cx, list);'),
 # ---- the lexer
 ("% after undef is the modulus", LEX, "(!afterValue() || (tokens.at(-1)?.kind === 'word' && tokens.at(-1)!.text === 'undef'", "(!afterValue() || (false && tokens.at(-1)?.kind === 'word' && tokens.at(-1)!.text === 'undef'"),
 ("\\E with nothing open is taken", LEX, "                    if (run() === undefined) refuse(", "                    if (run() === undefined) return true;\n                    if (false) refuse("),
 ("a run in a run is taken", LEX, "                    if (open !== undefined) refuse(`\\\\${c} inside a", "                    if (false) refuse(`\\\\${c} inside a"),
 ("\\u first in a run applies inside it", LEX, "                    stack.pop();\n                    flush(top());\n                    stack.push({ op, run: false, pieces: [], value: '', pos: where }, open);", "                    stack.push({ op, run: false, pieces: [], value: '', pos: where });"),
 ("\\u covers one character's worth: the next piece", LEX, "                flush(top());\n                stack.push({ op, run: false, pieces: [], value: '', pos: where });\n                return true;\n            },", "                flush(top());\n                stack.push({ op, run: true, pieces: [], value: '', pos: where });\n                return true;\n            },"),
 ("=cut alone ends at once", LEX, "                const cut = !first && /^=cut(?![A-Za-z0-9_])/.test(text);", "                const cut = /^=cut(?![A-Za-z0-9_])/.test(text);"),
 ("=cutting ends POD", LEX, "                const cut = !first && /^=cut(?![A-Za-z0-9_])/.test(text);", "                const cut = !first && /^=cut/.test(text);"),
 ("a line directive in POD is taken", LEX, "                if (/^#[ \\t]*line[ \\t]+[0-9]/.test(text)) refuse(", "                if (false) refuse("),
 ("POD anywhere a line begins", LEX, "            if (!statementMayBegin()) refuse('a line that begins = and a word", "            if (false) refuse('a line that begins = and a word"),
 ("__END__ is a word", LEX, "                if (!statementMayBegin()) refuse(`${text} in the middle of a statement: perl ends the program there, and does not compile what came before it`, start);\n                break;", "                if (!statementMayBegin()) refuse(`${text} in the middle of a statement: perl ends the program there, and does not compile what came before it`, start);"),
 # ---- the parser
 ("scalar @a reads on", PARSE, "            if (bare) bareOperand(head, 'scalar @a');", "            if (bare) { /* reads on */ }"),
 ("$#a = N anywhere", PARSE, "                    if (statementAt === undefined || statementAt.line !== left.pos.line || statementAt.col !== left.pos.col || limit !== AND_ROW) {", "                    if (false) {"),
 ("$#a = N is a sub's value", PARSE, "        if (expr.kind === 'arrayop' && expr.op === '$#=') return { kind: 'block', body: [{ kind: 'do', expr, pos: head.pos }], pos: head.pos };", ""),
 ("undef @a assigns undef", PARSE, "                const value: Expr = whole ? { kind: 'list', items: [], pos: head.pos } : { kind: 'constant', name: 'undef', pos: head.pos };", "                const value: Expr = { kind: 'constant', name: 'undef', pos: head.pos };"),
 ("undef of a slice", PARSE, "                const one = target.kind === 'var' || target.kind === 'elem'", "                const one = target.kind === 'slice' || target.kind === 'var' || target.kind === 'elem'"),
 ("undef X, more", PARSE, "                if (!ends(after) && !isModifier(after)) refuse(`undef ... is a statement", "                if (false) refuse(`undef ... is a statement"),
 ("a my in do while's test", PARSE, "                if (t.kind === 'word' && NAMES.get(t.text)?.kind === 'my') refuse(", "                if (false) refuse("),
 ("a die in do while's test", PARSE, "                if (t.kind === 'word' && t.text === 'die') refuse(", "                if (false) refuse("),
 ("do while's test is no loop test", PARSE, "            const test = unit(head.pos, () => expression(Infinity), true);\n            if (isModifier(peek()))", "            const test = unit(head.pos, () => expression(Infinity));\n            if (isModifier(peek()))"),
 ("or is and", PARSE, "            const arm: Arm = word.text === 'or' ? { test: expr, negate: true, body: [rhs], pos: word.pos } : { test: expr, body: [rhs], pos: word.pos };", "            const arm: Arm = word.text === 'and' ? { test: expr, negate: true, body: [rhs], pos: word.pos } : { test: expr, body: [rhs], pos: word.pos };"),
 ("or die after a list assignment", PARSE, "            if (expr.kind === 'listassign' || (expr.kind === 'assign' && (expr.target.kind === 'array'", "            if (false && (expr.kind === 'assign' && (expr.target.kind === 'array'"),
 ("or die and a modifier", PARSE, "            if (!ends(after)) refuse(`${show(after)} after '${word.text} ${then.text} ...'", "            if (!ends(after) && !isModifier(after)) refuse(`${show(after)} after '${word.text} ${then.text} ...'"),
 ("or say", PARSE, "            && ((then.kind === 'word' && then.text === 'die') || thenName?.kind === 'return' || thenName?.kind === 'jump')) {", "            && ((then.kind === 'word' && then.text === 'die') || thenName?.kind === 'return' || thenName?.kind === 'jump' || thenName?.kind === 'statement')) {"),
 ("sort, a blank and a bracket", PARSE, "            if (!touching(i - 1)) refuse('sort, a blank and a bracket", "            if (false) refuse('sort, a blank and a bracket"),
 ("sort(...)[0]", PARSE, "            if (peek().kind === '[') refuse(\"'[' after sort(...)", "            if (false) refuse(\"'[' after sort(...)"),
 ("a concatenation's newline is not looked at", PARSE, "        if (e.kind === 'binary' && e.op === '.') return newlineAtEnd(e.right);", "        if (e.kind === 'binary' && e.op === '.') return false;"),
 ("any concatenation ends in a newline", PARSE, "        if (e.kind === 'binary' && e.op === '.') return newlineAtEnd(e.right);", "        if (e.kind === 'binary' && e.op === '.') return true;"),
 ("a sprintf's newline is not looked at", PARSE, "        if (e.kind === 'listop' && e.op === 'sprintf') { const f = e.args[0]; return f?.kind === 'str' && f.value.endsWith('\\n'); }", ""),
 ("a sprintf's newline anywhere", PARSE, "return f?.kind === 'str' && f.value.endsWith('\\n'); }", "return f?.kind === 'str' && f.value.includes('\\n'); }"),
 ("__LINE__ is the statement's", PARSE, "            if (head.text === '__LINE__') return { kind: 'int', text: String(head.pos.line), value: BigInt(head.pos.line), pos: head.pos };", "            if (head.text === '__LINE__') return { kind: 'int', text: String(statementAt?.line ?? head.pos.line), value: BigInt(statementAt?.line ?? head.pos.line), pos: head.pos };"),
 ("__FILE__ is -", PARSE, "                return { kind: 'str', text: '__FILE__', value: file, pos: head.pos };", "                return { kind: 'str', text: '__FILE__', value: '-', pos: head.pos };"),
 ("substr of four on an element", PARSE, "            if (target.kind !== 'var' || target.bracketed) refuse(`${head.text} of ${args.length} arguments changes", "            if (target.bracketed) refuse(`${head.text} of ${args.length} arguments changes"),
 ("substr of four as a value", PARSE, "            if (!alone) refuse(`${head.text} of ${args.length} arguments is a statement", "            if (false) refuse(`${head.text} of ${args.length} arguments is a statement"),
 ("scalar reverse is reverse", PARSE, "            return { kind: 'listop', op: 'scalar reverse', args: of.kind === 'listop' ? of.args : [], pos: head.pos };", "            return of;"),
 # ---- the resolver, the checker and the code generator
 ("a do while's block is a loop's", RESOLVE, "                round.push({ bare: only.pos, post: s.negate ? 'until' : 'while' });", "                round.push({ loop: s });"),
 ("a lone range freezes", RESOLVE, "            const lone = loneRange(s.items);\n            bind(", "            const lone = false;\n            bind("),
 ("D77 guards a lone range", CHECK, "    if (scalars.size > 0 && !lone) body.forEach(b => expressions(b, guard));", "    if (scalars.size > 0) body.forEach(b => expressions(b, guard));"),
 ("D166 holds for a lone range", CHECK, "        if (w.names.captured.has(v) && !lone) {", "        if (w.names.captured.has(v)) {"),
 ("joined or die takes no my", CHECK, "            checkExpr(w, arm.test, !s.modifier || s.joined === true);", "            checkExpr(w, arm.test, !s.modifier);"),
 ("a lone range under a plus is not seen", SHAPES, "export const loneRange = (items: readonly Expr[]): boolean => items.length === 1 && isRange(behind(items[0]!));", "export const loneRange = (items: readonly Expr[]): boolean => items.length === 1 && isRange(items[0]!);"),
 ("a range first in a list is lone", SHAPES, "export const loneRange = (items: readonly Expr[]): boolean => items.length === 1 && isRange(behind(items[0]!));", "export const loneRange = (items: readonly Expr[]): boolean => items.length > 0 && isRange(behind(items[0]!));"),
 ("$#{$r} = N through undef makes nothing", GEN, "            const kept = v.place ? temp(b, v.c) : v;\n            const c = box(b, e, true);", "            const kept = v.place ? temp(b, v.c) : v;\n            const c = box(b, e, false);"),
 ("do until tests as while", GEN, "            const after = genWhole(s.test, s.pos.line, out, c => [`if (${s.negate ? 'rt_is_true' : 'rt_is_false'}(cx, ${c})) break;`]);", "            const after = genWhole(s.test, s.pos.line, out, c => [`if (rt_is_false(cx, ${c})) break;`]);"),
 ("do while tests first", GEN, "                ...indent([...s.body.flatMap(t => genStmt(t, out)), '{', ...indent([...after.vars, ...after.code]), '}']),", "                ...indent(['{', ...indent([...after.vars, ...after.code]), '}', ...s.body.flatMap(t => genStmt(t, out))]),"),
 ("makesWhole forgets $#=", CHECK, "(e.op === 'push' || e.op === 'unshift' || e.op === 'splice' || e.op === '$#=')", "(e.op === 'push' || e.op === 'unshift' || e.op === 'splice')"),
 ("quotemeta is no word", NAMES, "    ['quotemeta', { kind: 'unary', rt: 'rt_quotemeta' }],\n", ""),
]

only = sys.argv[1:]
if only == ['--match']:
    for name, path, old, new in MUTATIONS:
        n = open(path).read().count(old)
        if n != 1:
            print(n, name)
    print(len(MUTATIONS), 'pieces of text looked for')
    sys.exit(0)
knobs = checks.knobs()
tests = []
MOVED = ['1255', '768', '2146', '209', '2636', '110', '158', '159', '2820', '2821', '3109', '3110', '3537', '762', '868', '972']
for src in sorted(glob.glob('t/6[012][0-9][0-9]-*.pl') + [p for n in MOVED for p in glob.glob(f't/{n}-*.pl')]):
    head = open(src, encoding='utf-8', errors='replace').read(1200)
    env = dict(os.environ)
    env.update(knobs)
    found = re.search(r'^# env: (.*)$', head, re.M)
    if found:
        env.update(pair.split('=', 1) for pair in found.group(1).split())
    tests.append((os.path.basename(src)[:-3], open(src[:-3] + '.expected', 'rb').read(), env, 'kind: refused' in head))
ran = [t for t in tests if not t[3]]

def passes(test, driver):
    name, expected, env, refused = test
    if driver is None:
        # The test's own C as it was compiled at the start, and the
        # runtime of the copy.
        if subprocess.run(['cc', '-o', f'build/mut/{name}', f'build/mut/{name}.o', 'build/mut/rt.o', '-lm'], capture_output=True).returncode:
            return False
    else:
        built = subprocess.run(['node', driver, '-o', f'build/mut/{name}', f't/{name}.pl'], capture_output=True)
        if refused:
            return built.stderr + f'exit: {built.returncode}\n'.encode() == expected
        if built.returncode:
            return False
    try:
        run = checks.run_capped(['sh', '-c', 'exec "$0" 2>&1', f'build/mut/{name}'], env, b'', 20)
    except checks.Runaway:
        return False
    if run is None:
        return False
    got = run.stdout + (f'exit: {run.returncode}\n'.encode() if run.returncode else b'')
    return got == expected

def golden(driver):
    which = ran if driver is None else tests
    with ThreadPoolExecutor(4) as pool:
        return [t[0] for t, ok in zip(which, pool.map(lambda t: passes(t, driver), which)) if not ok]

def unit(tree):
    """The step added no unit test of the runtime: none to fail."""
    return 0

def copy():
    shutil.rmtree('build/mut/tree', ignore_errors=True)
    for part in ('bin', 'compiler/src', 'runtime'):
        shutil.copytree(part, 'build/mut/tree/' + part)

def runtime():
    """The copy's runtime, compiled; whether it compiled."""
    return subprocess.run(['cc', '-O1', '-c', '-Ibuild/mut/tree/runtime', '-o', 'build/mut/rt.o', 'build/mut/tree/runtime/rt.c'], capture_output=True).returncode == 0

os.makedirs('build/mut', exist_ok=True)
# The driver of a broken compiler links a runtime built once (CURLY_RT_OBJ),
# from the copy as it is first made: no compiler breakage touches it.
os.environ['CURLY_RT_OBJ'] = os.path.abspath('build/mut/rt-driver.o')
if os.path.exists(os.environ['CURLY_RT_OBJ']):
    os.remove(os.environ['CURLY_RT_OBJ'])
copy()
whole, units = golden('build/mut/tree/bin/curlyc.ts'), unit('build/mut/tree')
assert whole == [] and units == 0, f'things as they are fail: {whole}, {units} unit tests'
for name, _, _, _ in ran:
    subprocess.run(['cc', '-O0', '-c', '-Iruntime', '-o', f'build/mut/{name}.o', f'build/mut/{name}.c'], check=True)
assert runtime() and golden(None) == []
print(f'{len(tests)} golden tests and the unit tests pass as things are', flush=True)
missed = []
for name, path, old, new in MUTATIONS:
    if only and not any(o in name for o in only):
        continue
    copy()
    text = open(path).read()
    assert text.count(old) == 1, (name, text.count(old))
    open('build/mut/tree/' + path, 'w').write(text.replace(old, new))
    if path in (RT, MORE, HDR):
        # (A change to rt.h changes the generated code's view too: the
        # tests are compiled again by the copy's compiler and runtime.)
        if path == HDR:
            kept = os.environ['CURLY_RT_OBJ']
            os.environ['CURLY_RT_OBJ'] = os.path.abspath('build/mut/rt-header.o')
            if os.path.exists(os.environ['CURLY_RT_OBJ']):
                os.remove(os.environ['CURLY_RT_OBJ'])
            failed = golden('build/mut/tree/bin/curlyc.ts') if runtime() else ['the runtime does not compile']
            os.environ['CURLY_RT_OBJ'] = kept
        else:
            failed = golden(None) if runtime() else ['the runtime does not compile']
        units = unit('build/mut/tree')
    else:
        failed = golden('build/mut/tree/bin/curlyc.ts')
        units = 0
    if failed or units:
        print(f'{name}: golden {len(failed)} ({", ".join(f[:4] for f in failed[:6])}), unit {units}', flush=True)
    else:
        print(f'{name}: golden 0, unit 0   <-- NOT CAUGHT', flush=True)
        missed.append(name)
print(f'{len(missed)} not caught: {missed}')
