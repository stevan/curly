#!/usr/bin/env python3
"""Break step 14 on purpose, one way at a time, in the runtime and in each
pass of the compiler, and see that a test goes red each time: subs with no
name, what they capture, calls through a reference, `\\&name`, `__SUB__`,
the freeze for good, and the walks that see a call through a reference as
a call of any sub a reference can be to (D160 to D166).

    python3 docs/briefs/step14-mutations.py            # all of them
    python3 docs/briefs/step14-mutations.py "capture"  # those named so
    python3 docs/briefs/step14-mutations.py --match    # only see that each piece of text is there

Nothing in the tree is written: a broken runtime or compiler is a copy of
bin/, compiler/src/ and runtime/ under build/mut/tree/. Each breakage is
run two ways, and is caught if either goes red:

  golden   every test of step 14, t/3400*.pl to t/3599*.pl, the refused
           ones too, and 999 and 1926, run with the knobs of t/knobs.sh and
           each test's own `# env:`, as t/run.sh runs them
  unit     the runtime's own tests of subs' references, in the copy

A record of step 14, and not part of make test: each breakage is a piece of
the text as it was then, and one that no longer matches stops the run."""
import subprocess, glob, sys, os, shutil, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, 't')
import checks

RT = 'runtime/rt.c'
REF = 'runtime/ref.c'
HDR = 'runtime/rt.h'
UNWIND = 'runtime/unwind.c'
GEN = 'compiler/src/codegen.ts'
RESOLVE = 'compiler/src/resolver.ts'
CHECK = 'compiler/src/checker.ts'
PARSE = 'compiler/src/parser.ts'
LEX = 'compiler/src/lexer.ts'
SHAPES = 'compiler/src/shapes.ts'
MUTATIONS = [
 # ---- the runtime
 ("the collector does not walk a sub's reference", RT, "case RT_TAG_CELL: case RT_TAG_SREF: case RT_TAG_CODE:\n        mark_container", "case RT_TAG_CELL: case RT_TAG_SREF:\n        mark_container"),
 ("a sub's reference is a string", HDR, "return tag == RT_TAG_AREF || tag == RT_TAG_HREF || tag == RT_TAG_SREF || tag == RT_TAG_CODE;", "return tag == RT_TAG_AREF || tag == RT_TAG_HREF || tag == RT_TAG_SREF;"),
 ("a sub's reference is a number", RT, "    case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_SREF: case RT_TAG_CODE:\n        rt_fault(cx, \"a reference where a number is wanted\");", "    case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_SREF:\n        rt_fault(cx, \"a reference where a number is wanted\");"),
 ("a sub's reference is false", RT, "case RT_TAG_SREF: case RT_TAG_CODE: return 1;", "case RT_TAG_SREF: return 1;"),
 ("ref of a sub's reference is empty", REF, "    if (v.tag == RT_TAG_CODE) return rt_string(&STR_CODE);\n", ""),
 ("calling undef calls nothing", REF, "    if (v.tag == RT_TAG_UNDEF) rt_fault(cx, UNDEF_REFERENCE);\n    if (v.tag != RT_TAG_CODE) {", "    if (v.tag != RT_TAG_CODE) {"),
 ("calling what is no sub says undef", REF, "        rt_fault(cx, NOT_SUB);", "        rt_fault(cx, UNDEF_REFERENCE);"),
 ("a capture is not stored", REF, "    code.as.a->items[at + 1] = v;", "    (void)v;"),
 ("captures start at the function", HDR, "#define RT_CAPTURES(v) ((v)->as.a->items + 1)", "#define RT_CAPTURES(v) ((v)->as.a->items)"),
 ("the freeze for good is given back", REF, "    a->frozen |= FROZEN_FOREVER;", "    (void)a;"),
 ("the freeze for good of what a chain reached is not made", REF, "    for (uint64_t n = 0; n < a->count; n++) rt_freeze_forever(cx, a->items[n]);", "    (void)a;"),
 ("a sub's reference is thrown as a message", UNWIND, "if (a->count == 1 && rt_ref_tag(a->items[0].tag)) rt_throw", "if (a->count == 1 && a->items[0].tag != RT_TAG_CODE && rt_ref_tag(a->items[0].tag)) rt_throw"),
 # ---- the lexer
 ("->( is refused", LEX, "                if (next === '(') {\n                    push({ kind: 'op', text: op, pos: start });\n                    continue;\n                }", "                if (next === '(') refuse('->(', start);"),
 ("\\& is refused", LEX, "            if (op === '&' && last?.kind === 'op' && last.text === '\\\\' && between === '') {", "            if (false) {"),
 ("& before a value is bitwise", LEX, "            if (op === '&' && !afterValue()) refuse(", "            if (false) refuse("),
 ("->&* is taken for a name", LEX, "                if (src.startsWith('&*', i)) refuse(", "                if (false) refuse("),
 ("an anonymous signature is no signature", LEX, "            if (c === '(' && (signature > 0 || anon || (word?.kind", "            if (c === '(' && (signature > 0 || (word?.kind"),
 ("a sub's block ends no value", LEX, "last.deref === true || last.sub === true))", "last.deref === true))"),
 ("a sub's block after its signature is a hash's", LEX, "(name?.kind === ')' && anonClosed === tokens.length - 1))) {", "false)) {"),
 ("__SUB__ ends no value", LEX, "(NAMES.get(last.text)?.kind === 'constant' || NAMES.get(last.text)?.kind === 'cursub')", "NAMES.get(last.text)?.kind === 'constant'"),
 # ---- the parser
 ("a sub with no name is refused as a value", PARSE, "        if (name?.kind === 'sub') {\n            const open = peek();", "        if (name?.kind === 'sub') {\n            refuse('sub', t.pos);\n            const open = peek();"),
 ("a sub with no name sees no return", PARSE, "            const outer = { inSub, blocks, inList };\n            inSub = true;", "            const outer = { inSub, blocks, inList };\n            inSub = false;"),
 ("a sub with no name in a map's block may not return", PARSE, "            inSub = true;\n            blocks = 0;", "            inSub = true;"),
 ("an attribute is a signature", PARSE, "            if (open.kind !== '(' && open.kind !== '{') refuse(`after sub comes its signature or its block", "            if (false) refuse(`after sub comes its signature or its block"),
 ("a statement may not begin with a sub with no name", PARSE, "        if (name?.kind === 'sub' && tokens[i + 1]!.kind !== '{' && tokens[i + 1]!.kind !== '(') {", "        if (name?.kind === 'sub') {"),
 ("->( makes no call", PARSE, "                const call: CallRef = { kind: 'callref', head: e, args: callArguments(), pos: e.pos };\n                e = call;\n                continue;", "                callArguments();\n                continue;"),
 ("the arrow may not be left out", PARSE, "            const callable_ = subscripted || e.kind === 'callref';", "            const callable_ = false;"),
 ("the arrow may be left out after a variable", PARSE, "            if (e.kind === 'var' && t.kind === '(' && touching(i - 1)) refuse(", "            if (false) refuse("),
 ("the arrow may be left out after a call by name", PARSE, "            if (e.kind === 'invoke' && t.kind === '(') refuse(", "            if (false) refuse("),
 ("a blank before a call's bracket is taken", PARSE, "                if (t.kind === '(' && !touching(i - 1)) refuse(", "                if (false) refuse("),
 ("a key hard after a call is taken", PARSE, "            if (e.kind === 'callref' && t.kind === '{' && touching(i - 1)) refuse(", "            if (false) refuse("),
 ("a call through a reference is no arrow's head", PARSE, "        || e.kind === 'callref' || e.kind === 'anonsub' || e.kind === 'cursub';", "        || e.kind === 'anonsub' || e.kind === 'cursub';"),
 ("\\&name before an arrow is taken", PARSE, "                if (after.kind === '(' || after.kind === '[' || after.kind === '{' || (after.kind === 'op' && after.text.startsWith('->'))) {\n                    refuse(`${show(after)} after", "                if (false) {\n                    refuse(`${show(after)} after"),
 ("\\&name is refused", PARSE, "                return { kind: 'subref', name: word.text, pos: t.pos };", "                return refuse('subref', t.pos);"),
 ("__SUB__ is a word", PARSE, "            return stepAfter(chained({ kind: 'cursub', pos: t.pos }));", "            return refuse('cursub', t.pos);"),
 ("(EXPR)(...) is taken", PARSE, "            if (peek().kind === '(') refuse('a bracket after brackets", "            if (false) refuse('a bracket after brackets"),
 # ---- the resolver
 ("nothing is captured", RESOLVE, "            if (!captures[f]!.includes(id)) captures[f]!.push(id);", "            if (false) captures[f]!.push(id);"),
 ("only the innermost sub captures", RESOLVE, "        for (const f of nest.slice(nest.lastIndexOf(o) + 1)) {", "        for (const f of nest.slice(-1)) {"),
 ("a file variable is no use from outside", RESOLVE, "            uses[f] = true;\n            if (fileSlots.has(id)) continue;", "            if (fileSlots.has(id)) continue;\n            uses[f] = true;"),
 ("a sub with no name sees no outer variable", RESOLVE, "            scopes = [...scopes.map(scope => {", "            scopes = [fileScope, ...[].map(scope => {"),
 ("$_ is seen in a sub with no name", RESOLVE, "                for (const name of ['_', 'a', 'b']) if (seen_.delete(name)) hidden.add(name);", ""),
 ("last may leave a sub with no name", RESOLVE, "            round = [{ wall: 'anon' }];", "            round = [];"),
 ("__SUB__ is taken outside a sub with no name", RESOLVE, "            if (!isAnon[fn]) return refuse(\"__SUB__ outside", "            if (false) return refuse(\"__SUB__ outside"),
 ("\\&name of no sub is taken", RESOLVE, "            if (found === undefined) return refuse(`\\\\&${e.name}: the program has no sub", "            if (false) return refuse(`\\\\&${e.name}: the program has no sub"),
 ("no sub is one value", RESOLVE, "filter(f => (isAnon[f] && !uses[f]) || referred.has(f))", "filter(f => referred.has(f))"),
 ("a named sub is no target", RESOLVE, "const targets = [...subs.keys()].map(k => k + 1).filter(f => isAnon[f] || referred.has(f));", "const targets = [...subs.keys()].map(k => k + 1).filter(f => isAnon[f]);"),
 ("a loop's variable is not known", RESOLVE, "        if (binder.kind === 'foreach') loopVars.set(of.get(binder.var)!, held);", ""),
 ("the loop's list is read into the sub's", RESOLVE, "        const lists = naming.splice(0);", "        const lists: Set<number>[] = [];"),
 # ---- shapes
 ("a call through a reference gives no list", SHAPES, "    return ((e.kind === 'invoke' || e.kind === 'callref') && gives(e))", "    return (e.kind === 'invoke' && gives(e))"),
 ("a sub with no name gives no list", SHAPES, "call.kind === 'invoke' ? lists[calls.get(call)!] === true : targets.some(t => lists[t] === true)", "call.kind === 'invoke' ? lists[calls.get(call)!] === true : false"),
 # ---- the checker
 ("a call through a reference changes nothing", CHECK, "    e.kind === 'invoke' ? w.changed[w.names.calls.get(e)!]! : new Set(w.names.targets.flatMap(t => [...w.changed[t]!]));", "    e.kind === 'invoke' ? w.changed[w.names.calls.get(e)!]! : new Set<number>();"),
 ("a call through a reference has no defaults", CHECK, "    e.kind === 'invoke' ? w.defaults[w.names.calls.get(e)!]! : new Set(w.names.targets.flatMap(t => [...w.defaults[t]!]));", "    e.kind === 'invoke' ? w.defaults[w.names.calls.get(e)!]! : new Set<number>();"),
 ("the head is no part of its call", CHECK, "    : e.kind === 'callref' ? [...e.args, e.head]", "    : e.kind === 'callref' ? e.args"),
 ("a call through a reference is not ordered", CHECK, "        checkOrder(w, 'a call through a reference', [...e.args, e.head],", "        checkOrder(w, 'a call through a reference', [],"),
 ("a sub with no name is not checked", CHECK, "    if (e.kind === 'anonsub') checkSub(w, e.sub);", ""),
 ("a captured variable's store is the sub's own", CHECK, "if (id === REACH || id === CELLS || names.owner[id] !== fn) own[fn]!.add(id);", "if (id === REACH || id === CELLS || names.owner[id] === 0) own[fn]!.add(id);"),
 ("a call through a reference calls nothing", CHECK, "        if (e.kind === 'callref') names.targets.forEach(t => callees[fn]!.add(t));\n", ""),
 ("a concatenation's call through a reference is not seen", CHECK, "    if (e.kind === 'invoke' || e.kind === 'callref') into.push(e);", "    if (e.kind === 'invoke') into.push(e);"),
 ("a loop's block may call through a reference", CHECK, "        if (e.kind === 'invoke' || e.kind === 'callref') for (const id of calleeChanges(w, e)) if (scalars.has(id)) refused(id, e);", "        if (e.kind === 'invoke') for (const id of calleeChanges(w, e)) if (scalars.has(id)) refused(id, e);"),
 ("a loop's variable may be taken whatever its list", CHECK, "        if (w.names.captured.has(v)) {", "        if (false) {"),
 ("a sub with no name may store to a loop's variable", CHECK, "    names.subs.filter(s => s.anon).forEach(s => {", "    [].forEach((s: Sub) => {"),
 ("a call through a reference only has a value", CHECK, "s.expr.kind === 'invoke' || s.expr.kind === 'callref'", "s.expr.kind === 'invoke'"),
 # (Three more were run, and are taken out: nothing in the language can see
 # them. A file variable captured as well as reached through the context is
 # the same variable either way; the resolver reading what stands before
 # the arrow before the arguments changes no name, since neither may
 # declare one; and the order of a call's parts in `parts` is read by no
 # walk that cares, `checkOrder` building its own.)
 # ---- the code generator
 ("a captured scalar lives in no cell", GEN, "const inCell = (names: Resolution, id: number): boolean => (names.taken.has(id) || names.captured.has(id)) && !names.isArray[id];", "const inCell = (names: Resolution, id: number): boolean => names.taken.has(id) && !names.isArray[id];"),
 ("a capture is read from the file", GEN, "    return k >= 0 ? `RT_CAPTURES(self)[${k}]` : `g[${slot}]`;", "    return `g[${slot}]`;"),
 ("a loop's variable is one cell for the loop", GEN, "        const wrap = inCell(out.names, out.names.of.get(s.var)!) ? [`    rt_cell_wrap(cx, &${x});`] : [];", "        const wrap: string[] = [];"),
 ("a sub with no name is always one value", GEN, "        if (one !== undefined) return temp(b, slotOfId(b.names, b.fn, one));\n        const caps", "        if (one !== undefined || true) return temp(b, `rt_code_new(cx, ${cFn(b.names, n)}, 0)`);\n        const caps"),
 ("a sub that uses nothing is new each time", GEN, "        if (one !== undefined) return temp(b, slotOfId(b.names, b.fn, one));\n        const caps", "        if (one !== undefined) return temp(b, `rt_code_new(cx, ${cFn(b.names, n)}, 0)`);\n        const caps"),
 ("nothing is frozen for good", GEN, "            held.arrays.forEach(a => b.lines.push(`rt_freeze_forever(cx, ${slotOfId(b.names, b.fn, a)});`));", ""),
 ("a chain's containers are not frozen for good", GEN, "            if (held.frozen !== undefined) b.lines.push(`rt_freeze_all_forever(cx, ${slotOfId(b.names, b.fn, held.frozen)});`);", ""),
 ("the reference called is in no slot", GEN, "        const code = temp(b, `rt_code(cx, ${head.c})`);\n        const result = temp(b, `RT_CODE_FN(${code.c})(cx, ${WANT[want]}, ac${n}, av${n}, fl${n}, &${code.c})`);", "        b.lines.push(`rt_code(cx, ${head.c});`);\n        const result = temp(b, `RT_CODE_FN(${head.c})(cx, ${WANT[want]}, ac${n}, av${n}, fl${n}, (rt_value *)&${head.c})`);"),
 ("the head is worked out before the arguments", GEN, "        const n = genArguments(e.args, Math.max(1, e.args.length), b);\n        const head = genExpr(e.head, b);", "        const head = genExpr(e.head, b);\n        const n = genArguments(e.args, Math.max(1, e.args.length), b);"),
 ("the caller's context is not handed on", GEN, "        const result = temp(b, `RT_CODE_FN(${code.c})(cx, ${WANT[want]},", "        const result = temp(b, `RT_CODE_FN(${code.c})(cx, RT_LIST,"),
 ("the line is not stored again", GEN, "fl${n}, &${code.c})`);\n        b.lines.push(`cx->line = ${b.line};`);", "fl${n}, &${code.c})`);"),
 ("__SUB__ is undef", GEN, "    case 'cursub': return temp(b, '*self');", "    case 'cursub': return temp(b, 'rt_undef()');"),
 ("an anonymous sub is named as a named one", GEN, "const label = (s: Sub): string => (s.anon ? 'an anonymous sub' : s.name);", "const label = (s: Sub): string => s.name;"),
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
for src in sorted(glob.glob('t/3[45][0-9][0-9]-*.pl') + glob.glob('t/999-*.pl') + glob.glob('t/1926-*.pl')):
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
    """How many of the runtime's own tests of subs' references fail, in the copy."""
    r = subprocess.run(['node', '--test', '--test-name-pattern', "sub's reference", f'{tree}/runtime/tests/rt.test.ts'], capture_output=True, text=True)
    return len(re.findall(r'^not ok', r.stdout, re.M)) if r.returncode else 0

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
    if path in (RT, REF, UNWIND, HDR):
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
