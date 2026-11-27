#!/usr/bin/env python3
"""Break step 13b on purpose, one way at a time, in the runtime and in each
pass of the compiler, and see that a test goes red each time: the whole
container through a reference, read and changed, what a store makes, its
slices, the freeze of what a loop goes through, and the walks over names
that know what references reach (D108, D109, D114).

    python3 docs/briefs/step13b-mutations.py            # all of them
    python3 docs/briefs/step13b-mutations.py "freeze"   # those named so
    python3 docs/briefs/step13b-mutations.py --match    # only see that each piece of text is there

Nothing in the tree is written: a broken runtime or compiler is a copy of
bin/, compiler/src/ and runtime/ under build/mut/tree/. Each breakage is
run two ways, and is caught if either goes red:

  golden   every test of step 13b, t/2000*.pl to t/2199*.pl, the refused
           ones too, and 1915 to 1922, run with the knobs of t/knobs.sh
           and each test's own `# env:`, as t/run.sh runs them
  unit     the runtime's own tests of references, in the copy

A record of step 13b, and not part of make test: each breakage is a piece
of the text as it was then, and one that no longer matches stops the
run."""
import subprocess, glob, sys, os, shutil, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, 't')
import checks

RT = 'runtime/rt.c'
REF = 'runtime/ref.c'
HASH = 'runtime/hash.c'
GEN = 'compiler/src/codegen.ts'
RESOLVE = 'compiler/src/resolver.ts'
CHECK = 'compiler/src/checker.ts'
PARSE = 'compiler/src/parser.ts'
LEX = 'compiler/src/lexer.ts'
SHAPES = 'compiler/src/shapes.ts'
MUTATIONS = [
 # ---- the runtime (13b added nothing to it: these are what it leans on)
 ("a variable made is always an array", REF, "    rt_value c = made_container(cx, hash);\n    *slot = reference_to(c);", "    rt_value c = made_container(cx, 0);\n    *slot = reference_to(c);"),
 ("a push changes a frozen array", RT, "rt_value rt_push(rt_ctx *cx, rt_value array, rt_value list) {\n    changing(cx, array);", "rt_value rt_push(rt_ctx *cx, rt_value array, rt_value list) {"),
 ("an assignment changes a frozen array", RT, "void rt_array_assign(rt_ctx *cx, rt_value array, rt_value list) {\n    rt_array *a = changing(cx, array);", "void rt_array_assign(rt_ctx *cx, rt_value array, rt_value list) {\n    rt_array *a = array_of(cx, array);"),
 ("the rest of a list assignment changes a frozen array", RT, "void rt_array_rest(rt_ctx *cx, rt_value array, rt_value list, int64_t n) {\n    rt_array *a = changing(cx, array);", "void rt_array_rest(rt_ctx *cx, rt_value array, rt_value list, int64_t n) {\n    rt_array *a = array_of(cx, array);"),
 ("a hash assigned changes when frozen", HASH, "void rt_hash_rest(rt_ctx *cx, rt_value hash, rt_value list, int64_t n) {\n    rt_array *h = hash_changing(cx, hash);", "void rt_hash_rest(rt_ctx *cx, rt_value hash, rt_value list, int64_t n) {\n    rt_array *h = hash_of(cx, hash);"),
 ("an odd list for a hash is let through", HASH, "    if ((from->count - first) % 2 != 0) rt_fault(cx, \"an odd number of values for a hash\");\n", ""),
 # ---- the lexer
 ("the braces of a dereference end no value", LEX, "            || (last?.kind === '}' && (last.subscript === true || last.anon === true || last.deref === true))", "            || (last?.kind === '}' && (last.subscript === true || last.anon === true))"),
 ("a postfix form ends no value", LEX, "            || (last?.kind === 'op' && WHOLE.has(last.text))\n", "\n"),
 ("a word alone in the braces is taken", LEX, "        if (isWordStart(src[first] ?? '') && src[past(wordEnd(first), true)] === '}') {\n            refuse(`a word alone in ${sigil}", "        if (false) {\n            refuse(`a word alone in ${sigil}"),
 ("a word alone is looked for on one line", LEX, "        if (isWordStart(src[first] ?? '') && src[past(wordEnd(first), true)] === '}') {", "        if (isWordStart(src[first] ?? '') && src[past(wordEnd(first), false)] === '}') {"),
 ("a brace first in the braces is taken", LEX, "        if (src[first] === '{') refuse(`'{' first in the braces", "        if (false) refuse(`'{' first in the braces"),
 ("empty braces are taken", LEX, "        if (src[first] === '}') refuse(`${sigil}{} has nothing", "        if (false) refuse(`${sigil}{} has nothing"),
 ("a subscript after the braces is read", LEX, "                    if (src[after] === '[' || src[after] === '{') refuse(`a subscript after the braces", "                    if (false) refuse(`a subscript after the braces"),
 ("a subscript after the braces is looked for hard against them", LEX, "                    const after = past(i, true);\n                    if (src[after] === '[' || src[after] === '{') refuse(`a subscript after the braces", "                    const after = i;\n                    if (src[after] === '[' || src[after] === '{') refuse(`a subscript after the braces"),
 ("an arrow after the braces is read", LEX, "                    if (src.startsWith('->', after)) refuse(\"an arrow after the braces", "                    if (false) refuse(\"an arrow after the braces"),
 ("a subscript after a postfix form is read", LEX, "                    if (src[after] === '[' || src[after] === '{' || src.startsWith('->', after)) refuse(`a subscript after ->${whole}", "                    if (false) refuse(`a subscript after ->${whole}"),
 ("a slice's brace is no key's", LEX, "                || (name?.kind === 'op' && (name.text === '->' || name.text === '->@'));", "                || (name?.kind === 'op' && name.text === '->');"),
 ("%{ is a hash's name", LEX, "            if (at() === '{') {\n                cast('%', start);\n                continue;\n            }", "            if (at() === '{') refuse('%{', start);"),
 # ---- the parser
 ("->%* is an array", PARSE, "                return t.text === '->%*' ? { ...d, hash: true } : t.text === '->$#*' ? { ...d, last: true } : d;", "                return t.text === '->$#*' ? { ...d, last: true } : d;"),
 ("->$#* is the array", PARSE, "                return t.text === '->%*' ? { ...d, hash: true } : t.text === '->$#*' ? { ...d, last: true } : d;", "                return t.text === '->%*' ? { ...d, hash: true } : d;"),
 ("%{ } is an array", PARSE, "            return t.text === '%' ? { ...d, hash: true } : t.text === '$#' ? { ...d, last: true } : d;", "            return t.text === '$#' ? { ...d, last: true } : d;"),
 ("a slice through a reference is always an array's", PARSE, "                const hash = open.kind === '{';\n                const indexes = itemsTo(hash ? '}' : ']');", "                const hash = false;\n                const indexes = itemsTo(open.kind === '{' ? '}' : ']');"),
 ("a subscript after a slice through a reference is read", PARSE, "                if (after.kind === '[' || after.kind === '{' || (after.kind === 'op' && after.text.startsWith('->'))) refuse('a subscript after a slice: perl takes it", "                if (false) refuse('a subscript after a slice: perl takes it"),
 ("a builtin is given no container through a reference", PARSE, "        const may = t.kind === 'var' || t.kind === 'cast'", "        const may = t.kind === 'cast'"),
 ("keys of an array through a reference", PARSE, "                if (d?.kind !== 'deref' || !d.hash) return refuse(`${head.text} names a hash", "                if (d?.kind !== 'deref') return refuse(`${head.text} names a hash"),
 ("push onto the last index", PARSE, "        if (array.kind !== 'array' && (d?.kind !== 'deref' || d.hash || d.last)) return refuse(", "        if (array.kind !== 'array' && d?.kind !== 'deref') return refuse("),
 ("scalar of a hash through a reference is an array's count", PARSE, "        if (d !== undefined && name.shape === 'scalar' && d.kind === 'deref' && d.hash) {", "        if (false) {"),
 ("delete of a slice through a reference is refused", PARSE, "            } else if (op === 'delete' && element?.kind === 'slice' && element.deref !== undefined && element.hash) {", "            } else if (false) {"),
 ("++ of the whole container is taken", PARSE, "            if (target.kind !== 'var' && target.kind !== 'elem' && target.kind !== 'chain') return refuse(`'${t.text}' is for a variable or an element", "            if (false) return refuse(`'${t.text}' is for a variable or an element"),
 ("\\ before a dereference is taken", PARSE, "            if ((what.kind === 'var' && after.kind === 'op' && (WHOLE_OPS.has(after.text) || after.text === '->@')) || what.kind === 'cast') {", "            if (false) {"),
 ("sort $r->@* is a comparator", PARSE, "        if (first.kind === 'var' && !(arrow.kind === 'op' && arrow.text.startsWith('->') && touching(i))) refuse(", "        if (first.kind === 'var') refuse("),
 ("sort $r ->@* is a list", PARSE, "        if (first.kind === 'var' && !(arrow.kind === 'op' && arrow.text.startsWith('->') && touching(i))) refuse(", "        if (first.kind === 'var' && !(arrow.kind === 'op' && arrow.text.startsWith('->'))) refuse("),
 ("brackets round a value take no postfix form", PARSE, "            if (!isList && peek().kind === 'op' && peek().text.startsWith('->')) return stepAfter(chained(inner));", "            if (!isList && peek().kind === 'op' && peek().text === '->') return stepAfter(chained(inner));"),
 ("the whole container is assigned as a list", PARSE, "                if (left.kind === 'array' || left.kind === 'myarray' || (left.kind === 'deref' && !left.last)) {", "                if (left.kind === 'array' || left.kind === 'myarray') {"),
 ("the last index may be assigned", PARSE, "                if (left.kind !== 'var' && left.kind !== 'my' && left.kind !== 'elem' && left.kind !== 'chain') {", "                if (left.kind !== 'var' && left.kind !== 'my' && left.kind !== 'elem' && left.kind !== 'chain' && left.kind !== 'deref') {"),
 # ---- the resolver
 ("the whole container in a loop's list freezes nothing", RESOLVE, "        case 'deref':\n            walk(e.head, declared);\n            if (!quoted) chains.fill(true);", "        case 'deref':\n            walk(e.head, declared);"),
 ("a slice through a reference is looked up by name", RESOLVE, "            if (e.deref !== undefined) return walk(e.deref, declared);\n            return e.name === undefined ? undefined : array(e, e.name);", "            return e.name === undefined ? undefined : array(e, e.name);"),
 # ---- the checker
 ("the whole container names nothing", CHECK, "    else if (e.kind === 'deref') whole(e);\n", "\n"),
 ("the whole container names only its head", CHECK, "    const whole = (d: Deref): void => {\n        into.add(REACH);", "    const whole = (d: Deref): void => {"),
 ("a slice or values through a reference names nothing", CHECK, "    else if ((e.kind === 'slice' || (e.kind === 'hashop' && e.op === 'values')) && e.deref !== undefined) whole(e.deref);\n", "    else if ((e.kind === 'slice' || (e.kind === 'hashop' && e.op === 'values')) && e.deref !== undefined) undefined;\n"),
 ("a builtin through a reference changes nothing", CHECK, "    if (e.kind === 'arrayop' && e.op !== 'scalar' && e.deref !== undefined) return direct ? [] : makesWhole(e) ? [REACH, ...making(w, e.deref)] : [REACH];", "    if (e.kind === 'arrayop' && e.op !== 'scalar' && e.deref !== undefined) return [];"),
 ("a push through a reference makes nothing", CHECK, "const makesWhole = (e: Expr): boolean => e.kind === 'arrayop' && e.deref !== undefined && (e.op === 'push' || e.op === 'unshift' || e.op === 'splice');", "const makesWhole = (e: Expr): boolean => false && e.kind === 'arrayop';"),
 ("an assignment to the whole changes nothing", CHECK, "    if ((e.kind === 'assign' || e.kind === 'step') && (e.target.kind === 'chain' || e.target.kind === 'deref')) return direct ? [] : [REACH, ...making(w, e.target)];", "    if ((e.kind === 'assign' || e.kind === 'step') && e.target.kind === 'deref') return [];\n    if ((e.kind === 'assign' || e.kind === 'step') && e.target.kind === 'chain') return direct ? [] : [REACH, ...making(w, e.target)];"),
 ("a delete of a slice through a reference changes nothing", CHECK, "    if (e.kind === 'hashop' && e.op === 'delete' && (e.chain !== undefined || e.deref !== undefined)) return direct ? [] : [REACH];", "    if (e.kind === 'hashop' && e.op === 'delete' && e.deref !== undefined) return [];\n    if (e.kind === 'hashop' && e.op === 'delete' && e.chain !== undefined) return direct ? [] : [REACH];"),
 ("a list assignment to the whole changes nothing", CHECK, "            : t.kind === 'deref' ? (direct ? [] : [REACH, ...making(w, t)])", "            : t.kind === 'deref' ? []"),
 ("the whole container is made in its head's head", CHECK, "        if (head.kind === 'chain') {\n            making(w, head, into);\n            into.add(REACH);\n        }", "        if (head.kind === 'chain') {\n            into.add(REACH);\n        }"),
 ("making the whole is not checked against the right side", CHECK, "        checkMaking(w, e.target, e.value, true);\n    }\n    if (e.kind === 'listassign') {", "    }\n    if (e.kind === 'listassign') {"),
 ("a push's container is not first in its order", CHECK, "    if (e.kind === 'arrayop') checkOrder(w, e.op, [...(e.deref !== undefined ? [e.deref] : []), ...e.args], true);", "    if (e.kind === 'arrayop') checkOrder(w, e.op, e.args, true);"),
 ("the head in the braces is not checked", CHECK, "    case 'deref': return [[e.head, 'scalar']];", "    case 'deref': return [];"),
 ("defined of the whole container is taken", CHECK, "&& (of?.kind === 'array' || (of?.kind === 'deref' && !of.last))) {", "&& of?.kind === 'array') {"),
 ("a slice of one through a reference is refused", CHECK, "    if (e.kind !== 'slice' || e.name === undefined || e.deref !== undefined || e.indexes.length !== 1) return;", "    if (e.kind !== 'slice' || e.name === undefined || e.indexes.length !== 1) return;"),
 ("a push in a concatenation changes no name", CHECK, "    if (whole !== undefined && derefBase(whole).kind === 'var') into.add((derefBase(whole) as Var).name);", "    void whole;"),
 ("the whole container is one value in a list", CHECK, "    return e.kind === 'array' || e.kind === 'myarray' || (e.kind === 'deref' && !e.last) || e.kind === 'list'", "    return e.kind === 'array' || e.kind === 'myarray' || e.kind === 'list'"),
 # ---- what a sub gives
 ("a sub that gives the whole container gives one value", SHAPES, "    case 'deref': return e.last !== true;", "    case 'deref': return false;"),
 # ---- the code generator
 ("the whole container through a reference is never made", GEN, "    return genChain(whole, b, store).container;", "    return genChain(whole, b, false).container;"),
 ("a push's container is made after its list", GEN, "            const c = e.deref === undefined ? undefined : box(b, e, true);\n            const values = genList(e.args, b);", "            const values = genList(e.args, b);\n            const c = e.deref === undefined ? undefined : box(b, e, true);"),
 ("a push through a reference reads, and makes nothing", GEN, "            const c = e.deref === undefined ? undefined : box(b, e, true);", "            const c = e.deref === undefined ? undefined : box(b, e, false);"),
 ("splice makes nothing", GEN, "    const c = box(b, e, true);\n    const [offset, length]", "    const c = box(b, e, false);\n    const [offset, length]"),
 ("an assignment's container before its list", GEN, "            const values = genList([e.value], b);\n            const c = genDeref(e.target, b, true);", "            const c = genDeref(e.target, b, true);\n            const values = genList([e.value], b);"),
 ("a slice on the left is read, not made", GEN, "                containers[n] = box(b, t, true);", "                containers[n] = box(b, t, false);"),
 ("the whole container last among targets is read, not made", GEN, "            if (t.kind === 'deref') containers[n] = genDeref(t, b, true);", "            if (t.kind === 'deref') containers[n] = genDeref(t, b, false);"),
 ("keys through a reference freeze the hash", GEN, "        const c = e.op === 'keys' ? unfrozen(b, () => box(b, e, false)) : box(b, e, false);", "        const c = box(b, e, false);"),
 ("values through a reference freeze nothing", GEN, "        const c = e.op === 'keys' ? unfrozen(b, () => box(b, e, false)) : box(b, e, false);", "        const c = unfrozen(b, () => box(b, e, false));"),
 ("a count through a reference freezes the hash", GEN, "            const c = e.op === 'values' ? box(b, e, false) : unfrozen(b, () => box(b, e, false));", "            const c = box(b, e, false);"),
 ("a hash through a reference in a list is its keys", GEN, "        b.lines.push(`${e.hash ? 'rt_list_add_pairs' : 'rt_list_add_all'}(cx, ${list}, ${c});`);\n    } else if (e.kind === 'hashop' && e.keys !== undefined) {", "        b.lines.push(`${e.hash ? 'rt_list_add_keys' : 'rt_list_add_all'}(cx, ${list}, ${c});`);\n    } else if (e.kind === 'hashop' && e.keys !== undefined) {"),
 ("the last index through a reference is the count", GEN, "        return temp(b, `${e.last ? 'rt_last_index' : e.hash ? 'rt_hash_count' : 'rt_count'}(cx, ${c})`);", "        return temp(b, `${e.hash ? 'rt_hash_count' : 'rt_count'}(cx, ${c})`);"),
 ("the whole container is a list in a call's arguments only by name", GEN, "    return e.kind === 'array' || (e.kind === 'deref' && !e.last) || e.kind === 'list'", "    return e.kind === 'array' || e.kind === 'list'"),
 ("a slice through a reference in a loop's list is not strict", GEN, "            b.lines.push(`rt_list_add_slice(cx, ${list}, ${c}, ${indexes.c}, ${strict ? 2 : 0});`);", "            b.lines.push(`rt_list_add_slice(cx, ${list}, ${c}, ${indexes.c}, ${strict && e.deref === undefined ? 2 : 0});`);"),
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
for src in sorted(glob.glob('t/20[0-9][0-9]-*.pl') + glob.glob('t/21[0-9][0-9]-*.pl') + glob.glob('t/19[12][0-9]-*.pl')):
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
    """How many of the runtime's own tests of references fail, in the copy."""
    r = subprocess.run(['node', '--test', '--test-name-pattern', 'reference|arrow|hop|walks a chain', f'{tree}/runtime/tests/rt.test.ts'], capture_output=True, text=True)
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
    if path in (RT, REF, HASH):
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
