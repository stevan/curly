#!/usr/bin/env python3
"""Break step 17a on purpose, one way at a time, in the runtime and in each
pass of the compiler, and see that a test goes red each time: classes,
fields, methods, `new`, dispatch, the core, and the walks that see a method
call as a call of every method of its name and `new` as a call of every
default and `ADJUST` of its chain (D170 to D178, D187).

    python3 docs/briefs/step17a-mutations.py            # all of them
    python3 docs/briefs/step17a-mutations.py "field"    # those named so
    python3 docs/briefs/step17a-mutations.py --match    # only see that each piece of text is there

Nothing in the tree is written: a broken runtime or compiler is a copy of
bin/, compiler/src/ and runtime/ under build/mut/tree/. Each breakage is
run two ways, and is caught if either goes red:

  golden   every test of step 17a, t/4000*.pl to t/4399*.pl, the refused
           ones too, and 1925 and 3505, run with the knobs of t/knobs.sh and
           each test's own `# env:`, as t/run.sh runs them
  unit     the runtime's own tests of classes and objects, in the copy

A record of step 17a, and not part of make test: each breakage is a piece
of the text as it was then, and one that no longer matches stops the run."""
import subprocess, glob, sys, os, shutil, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, 't')
import checks

RT = 'runtime/rt.c'
REF = 'runtime/ref.c'
OBJ = 'runtime/obj.c'
HDR = 'runtime/rt.h'
UNWIND = 'runtime/unwind.c'
GEN = 'compiler/src/codegen.ts'
RESOLVE = 'compiler/src/resolver.ts'
CHECK = 'compiler/src/checker.ts'
PARSE = 'compiler/src/parser.ts'
LEX = 'compiler/src/lexer.ts'
SHAPES = 'compiler/src/shapes.ts'
NAMES_ = 'compiler/src/names.ts'
MUTATIONS = [
 # ---- the runtime
 ("the collector does not walk an object", RT, "case RT_TAG_SREF: case RT_TAG_CODE: case RT_TAG_OBJ:\n        mark_container", "case RT_TAG_SREF: case RT_TAG_CODE:\n        mark_container"),
 ("the core is no root", RT, "    for (int k = 0; k < 3; k++) mark(cx, cx->core[k]);\n", ""),
 ("an object is a string", HDR, "tag == RT_TAG_CODE || tag == RT_TAG_OBJ;", "tag == RT_TAG_CODE;"),
 ("an object is a number", RT, "    case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_SREF: case RT_TAG_CODE: case RT_TAG_OBJ:\n        rt_fault(cx, \"a reference where a number is wanted\");", "    case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_SREF: case RT_TAG_CODE:\n        rt_fault(cx, \"a reference where a number is wanted\");"),
 ("an object is false", RT, "case RT_TAG_CODE: case RT_TAG_OBJ: return 1;", "case RT_TAG_CODE: return 1;"),
 ("ref of an object is empty", REF, "    if (v.tag == RT_TAG_OBJ) return rt_class_name(cx, v);\n", ""),
 ("a field is at the class's place", HDR, "#define RT_FIELD(o, k) ((o).as.a->items[(k) + 1])", "#define RT_FIELD(o, k) ((o).as.a->items[(k)])"),
 ("calling undef says no object", OBJ, "    if (v.tag == RT_TAG_UNDEF) rt_fault(cx, UNDEF_OBJECT);\n    if (v.tag != RT_TAG_OBJ) {", "    if (v.tag != RT_TAG_OBJ) {"),
 ("calling what is no object says undef", OBJ, "        rt_fault(cx, NOT_OBJECT);", "        rt_fault(cx, UNDEF_OBJECT);"),
 ("a missing method says nothing of its name", OBJ, "snprintf(what, sizeof what, \"an object of %.*s has no method %.300s\"", "snprintf(what, sizeof what, \"an object of %.*s has no method\""),
 ("a parent's table is not copied", OBJ, "for (int64_t k = 0; k < methods && CLASS_TABLE + (uint64_t)k < p->count; k++) a->items[CLASS_TABLE + k] = p->items[CLASS_TABLE + k];", "(void)p;"),
 ("a method is not put in its table", OBJ, "    a->items[CLASS_TABLE + id] = fn_value(fn);", "    (void)fn;"),
 ("isa looks at the class alone", OBJ, "c = instance_of(cx, c)->items[CLASS_PARENT]) {", "c = rt_undef()) {"),
 ("isa of anything is true", OBJ, "    if (v.tag != RT_TAG_OBJ) return rt_bool(0);\n    rt_array *want", "    if (v.tag != RT_TAG_OBJ) return rt_bool(1);\n    rt_array *want"),
 ("blessed is a name for anything", OBJ, "    return v.tag == RT_TAG_OBJ ? rt_class_name(cx, v) : rt_undef();", "    return v.tag == RT_TAG_OBJ ? rt_class_name(cx, v) : rt_string(&STR_OBJECT);"),
 ("reftype of an object is undef", OBJ, "    if (v.tag == RT_TAG_OBJ) return rt_string(&STR_OBJECT);", "    if (v.tag == RT_TAG_OBJ) return rt_undef();"),
 ("an odd count is taken", OBJ, "    if (argc % 2 != 0) {", "    if (0) {"),
 ("a name twice is taken", OBJ, "        if (places[found] != NULL) {", "        if (0) {"),
 ("an unknown name is taken", OBJ, "        if (found < 0) {", "        if (found < 0) {\n            continue;"),
 ("a missing parameter is taken", OBJ, "        if (required[k] && places[k] == NULL) {", "        if (0) {"),
 ("a value is its name", OBJ, "        places[found] = flat != NULL ? &flat[n + 1] : argv[n + 1];", "        places[found] = flat != NULL ? &flat[n] : argv[n];"),
 ("the class of a class is no class", OBJ, "    cx->core[RT_CORE_CLASS].as.a->items[CLASS_OF] = cx->core[RT_CORE_CLASS];\n", ""),
 ("a constructor of __CLASS__ is the core's", OBJ, "    rt_value f = class_of(cx, obj)->items[CLASS_MAKER];", "    rt_value f = class_of(cx, class_of(cx, obj)->items[CLASS_PARENT])->items[CLASS_MAKER];"),
 # ---- names
 ("isa is no operator", NAMES_, "    { assoc: 'nonassoc', infix: [{ op: 'isa', in: true }] },", "    { assoc: 'nonassoc', infix: ops('isa') },"),
 ("floor is a method's name", NAMES_, "'ceil', 'floor', 'is_tainted', 'trim', 'indexed',\n    'STDIN'", "'ceil', 'is_tainted', 'trim', 'indexed',\n    'STDIN'"),
 ("Carp is a class's name", NAMES_, "    'CORE', 'Carp', 'DB',", "    'CORE', 'DB',"),
 ("the pragma is not in the list", NAMES_, "    ['experimental', { args: ['class'] }],", "    ['experimental', { args: ['signatures'] }],"),
 # ---- the lexer
 ("A::B is no word", LEX, "            while (src.startsWith('::', i) && isWordStart(src[i + 2] ?? '')) {", "            while (false) {"),
 ("a method's name may be an operator", LEX, "        return isArrow(a) || (a?.kind === 'word' && a.text === 'method')", "        return (a?.kind === 'word' && a.text === 'method')"),
 ("an operator after a method's name is a value", LEX, "            || (last?.kind === 'word' && isArrow(tokens.at(-2)));", "            || false;"),
 ("->& is refused", LEX, "                if (next === '&' && isWordStart(src[i + 1] ?? '')) {\n                    take();", "                if (next === '&' && isWordStart(src[i + 1] ?? '')) {\n                    refuse('->&', start);\n                    take();"),
 ("a method's signature is no signature", LEX, "(NAMES.get(word.text)?.kind === 'sub' || NAMES.get(word.text)?.kind === 'method') && name?.kind === 'word'", "NAMES.get(word.text)?.kind === 'sub' && name?.kind === 'word'"),
 # ---- the parser
 ("a method call has no arguments", PARSE, "        if (open.kind !== '(') return [];\n        if (!touching(i - 1)) refuse(`a blank between the method's name", "        if (open.kind !== '(' || true) return [];\n        if (!touching(i - 1)) refuse(`a blank between the method's name"),
 ("a blank before a method's bracket is taken", PARSE, "        if (!touching(i - 1)) refuse(`a blank between the method's name", "        if (false) refuse(`a blank between the method's name"),
 ("SUPER is no parent", PARSE, "                e = name.text.startsWith('SUPER::') ? { kind: 'methcall', invocant: e, name: method, args, super: true, pos: name.pos }", "                e = false ? { kind: 'methcall', invocant: e, name: method, args, super: true, pos: name.pos }"),
 ("->& dispatches", PARSE, "                    : lexical ? { kind: 'methcall', invocant: e, name: method, args, lexical: true, pos: name.pos }", "                    : false ? { kind: 'methcall', invocant: e, name: method, args, lexical: true, pos: name.pos }"),
 ("new on an object is taken", PARSE, "                if (!lexical && method === 'new') refuse(", "                if (false) refuse("),
 ("UNIVERSAL's methods are taken", PARSE, "                if (!lexical && ['isa', 'can', 'DOES', 'VERSION'].includes(method)) refuse(", "                if (false) refuse("),
 ("another class's method is taken", PARSE, "                if (name.text.includes('::') && !(name.text.startsWith('SUPER::')", "                if (false && !(name.text.startsWith('SUPER::')"),
 ("a class's method is new", PARSE, "        if (name.text !== 'new') {\n            refuse(`${shown}->${name.text}:", "        if (false) {\n            refuse(`${shown}->${name.text}:"),
 ("!$x isa P is taken", PARSE, "                if (first.kind === 'unary' && !first.bracketed && prefixOp(first.op)?.bang) refuse(`'${first.op}' before 'isa'", "                if (false) refuse(`'${first.op}' before 'isa'"),
 ("isa isa is taken", PARSE, "                if (peek().kind === 'op' && peek().text === 'isa') refuse(", "                if (false) refuse("),
 ("blessed before an operator is taken", PARSE, "(head.text === 'ref' || head.text === 'blessed' || head.text === 'reftype') && arg.kind === 'binary'", "head.text === 'ref' && arg.kind === 'binary'"),
 ("a field has no reader", PARSE, "                if (field.reader !== undefined) {\n                    const r = field.reader;", "                if (false) {\n                    const r = field.reader!;"),
 ("a writer gives what it stored", PARSE, "body: [store, { kind: 'do', expr: { kind: 'var', name: 'self', pos: w.pos }, pos: w.pos }]", "body: [store]"),
 ("a reader of an array is its count", PARSE, "const value: Expr = v.kind === 'my' ? { kind: 'var', name: v.name, pos: v.pos } : { kind: 'array', name: v.name, pos: v.pos, ...(v.hash ? { hash: true as const } : {}) };", "const value: Expr = v.kind === 'my' ? { kind: 'var', name: v.name, pos: v.pos } : { kind: 'arrayop', op: 'scalar', name: v.name, args: [], pos: v.pos, at: v.pos };"),
 ("a field's default is not in its fields' function", PARSE, "                if (field.default !== undefined) defaults.push({ kind: 'do', expr: field.default, pos: field.pos });", ""),
 ("a param on an array is taken", PARSE, "                if (v.kind !== 'var') refuse(`:param on ${v.text}", "                if (false) refuse(`:param on ${v.text}"),
 ("a blank after an attribute's colon is taken", PARSE, "        if (word.kind !== 'word' || !touching(i - 2)) return refuse(`an attribute is written hard against its colon", "        if (word.kind !== 'word') return refuse(`an attribute is written hard against its colon"),
 ("//= with no :param is taken", PARSE, "            if (op !== '=' && param === undefined) refuse(", "            if (false) refuse("),
 ("method m; is taken", PARSE, "                if (open.kind === ';') refuse(`method ${word.text}; with no block", "                if (false) refuse(`method ${word.text}; with no block"),
 ("a class may stand in a block", PARSE, "        if (depth > 0) refuse('a class stands at the top level of the file", "        if (false) refuse('a class stands at the top level of the file"),
 # ---- the resolver
 ("a field is seen above its declaration", RESOLVE, "                seenBy.set(b, new Map(inside.fields));\n                continue;", "                continue;"),
 ("a parent's fields are a child's", RESOLVE, "            function_(s.init, info.init, { cls: c, fields: new Map(), item: -1 });", "            function_(s.init, info.init, { cls: c, fields: new Map(info.parent < 0 ? [] : classes[info.parent]!.fields.map(f => [key(f.field.var), f.id] as [string, number])), item: -1 });"),
 ("a bare call in a class is the program's", RESOLVE, "            if (inClass >= 0 && bare === e.name && called.has(bare)) return refuse(", "            if (false) return refuse("),
 ("a name may hide a field", RESOLVE, "        if (inClass < 0 || d.name.startsWith(' ')) return;\n        const k", "        if (true) return;\n        const k"),
 ("$self may be assigned", RESOLVE, "        readonly.add(of.get(d)!);\n        selfOf[fn] = of.get(d);", "        selfOf[fn] = of.get(d);"),
 ("a method call reaches one method", RESOLVE, "            targetsOf.set(e, found);\n            return;", "            targetsOf.set(e, found.slice(0, 1));\n            return;"),
 ("SUPER is the class's own", RESOLVE, "                const fn = parent < 0 ? undefined : classes[parent]!.table.get(e.name);", "                const fn = parent < 0 ? undefined : classes[inClass]!.table.get(e.name);"),
 ("->& is taken above its my method", RESOLVE, "                if (lexical.item > inItem) return refuse(", "                if (false) return refuse("),
 ("new runs no ADJUST", RESOLVE, "                return [...all.map(k => classes[k]!.init), ...all.flatMap(k => classes[k]!.adjusts)];", "                return all.map(k => classes[k]!.init);"),
 ("__CLASS__->new runs no class below", RESOLVE, "                const below = classes.map((_, k) => k).filter(k => chain(k).includes(inClass));", "                const below = [inClass];"),
 ("a parameter's name may be a parent's", RESOLVE, "                if (taken_.has(q.name)) refuse(", "                if (false) refuse("),
 ("a method may have a reserved name", RESOLVE, "                if (METHOD_RESERVED.has(name)) refuse(", "                if (false) refuse("),
 ("a class's name may be lower case", RESOLVE, "            if (parts.some(p => !/^[A-Z]/.test(p))) refuse(", "            if (false) refuse("),
 ("a method may be named as a class", RESOLVE, "                if (classOf.has(b.name) || classOf.has(`${info.name}::${b.name}`)) {", "                if (false) {"),
 ("a method named twice is taken", RESOLVE, "                if (info.methods.has(name) || info.lexicals.has(name)) refuse(", "                if (false) refuse("),
 ("\\$self is taken", RESOLVE, "            if (e.of.kind === 'var' && e.of.name === 'self' && inClass >= 0) return refuse(", "            if (false) return refuse("),
 ("isa of no class is taken", RESOLVE, "            if (c === undefined) return refuse(`isa ${e.cls}: the program has no class", "            if (c === undefined) return;\n            if (false) return refuse(`isa ${e.cls}: the program has no class"),
 # ---- shapes
 ("a method call hands on no list", SHAPES, "    return (isCall(e) && gives(e))", "    return ((e.kind === 'invoke' || e.kind === 'callref') && gives(e))"),
 ("a method gives no list", SHAPES, "        : (targetsOf.get(call) ?? []).some(t => lists[t] === true));", "        : false);"),
 # ---- the checker
 ("the invocant is no part of its call", CHECK, "    : e.kind === 'methcall' ? [e.invocant, ...e.args]", "    : e.kind === 'methcall' ? e.args"),
 ("a method call is not ordered", CHECK, "        checkOrder(w, `the call of the method ${e.name}`, [e.invocant, ...e.args],", "        checkOrder(w, `the call of the method ${e.name}`, [],"),
 ("new's arguments are not ordered", CHECK, "        checkOrder(w, `the arguments of ${e.cls ?? '__CLASS__'}->new`, e.args,", "        checkOrder(w, `the arguments of ${e.cls ?? '__CLASS__'}->new`, [],"),
 ("new has no defaults", CHECK, "    e.kind === 'new' ? new Set(calleeTargets(w, e).filter(t => w.names.subs[t - 1]!.method?.how === 'init').flatMap(t => [...w.changed[t]!]))", "    e.kind === 'new' ? new Set<number>()"),
 ("a method call calls nothing", CHECK, "        if (e.kind === 'methcall' || e.kind === 'new') names.targetsOf.get(e)!.forEach(t => callees[fn]!.add(t));", ""),
 ("a method call changes nothing where it stands", CHECK, "    if (isCall(e)) calleeChanges(w, e).forEach(id => into.add(id));", "    if (e.kind === 'invoke' || e.kind === 'callref') calleeChanges(w, e).forEach(id => into.add(id));"),
 ("a concatenation's method call is not seen", CHECK, "    if (isCall(e)) into.push(e);", "    if (e.kind === 'invoke' || e.kind === 'callref') into.push(e);"),
 ("a loop's block may call a method", CHECK, "        if (isCall(e)) for (const id of calleeChanges(w, e)) if (scalars.has(id)) refused(id, e);", "        if (e.kind === 'invoke' || e.kind === 'callref') for (const id of calleeChanges(w, e)) if (scalars.has(id)) refused(id, e);"),
 ("a method's list is not seen", CHECK, "    : calleeTargets(w, call).some(t => w.names.lists[t] === true));", "    : false);"),
 ("a class needs no pragma", CHECK, "            if (!seen.has('experimental')) refuse(", "            if (false) refuse("),
 ("a field's default is not checked", CHECK, "        checkExpr(w, b.default, false, scalar ? 'scalar' : 'list');", ""),
 ("a method is not checked", CHECK, "        if (b.kind === 'sub') {\n            checkSub(w, b);\n            continue;\n        }", "        if (b.kind === 'sub') continue;"),
 # ---- the code generator
 ("the invocant is read early", GEN, "        const where = pointTo(b, inv);", "        const where = `&${temp(b, inv.c).c}`;"),
 ("the arguments come before the invocant", GEN, "        const inv = genExpr(e.invocant, b);\n        const where = pointTo(b, inv);\n        const kept = `iv${++b.temps}`;\n        b.decls.push(`rt_value *${kept} RT_UNUSED;`);\n        b.lines.push(`${kept} = ${where};`);\n        const n = genArguments(e.args, Math.max(1, e.args.length), b);",
  "        const n = genArguments(e.args, Math.max(1, e.args.length), b);\n        const inv = genExpr(e.invocant, b);\n        const where = pointTo(b, inv);\n        const kept = `iv${++b.temps}`;\n        b.decls.push(`rt_value *${kept} RT_UNUSED;`);\n        b.lines.push(`${kept} = ${where};`);"),
 ("a method is not handed its caller's context", GEN, "        const result = temp(b, `${call}(cx, ${WANT[want]}, ac${n}, av${n}, fl${n}, ${kept})`);", "        const result = temp(b, `${call}(cx, RT_LIST, ac${n}, av${n}, fl${n}, ${kept})`);"),
 ("the line is not stored again after a method", GEN, "fl${n}, ${kept})`);\n        b.lines.push(`cx->line = ${b.line};`);", "fl${n}, ${kept})`);"),
 ("$self is in no cell", GEN, "        lines.push(`${slot} = *self; // $self`, ...(inCell(names, selfId) ? [`rt_cell_wrap(cx, &${slot});`] : []));", "        lines.push(`${slot} = *self; // $self`);"),
 ("a scalar field is no cell", GEN, "(names.taken.has(id) || names.captured.has(id) || names.fieldOf.has(id)) && !names.isArray[id]", "(names.taken.has(id) || names.captured.has(id)) && !names.isArray[id]"),
 ("an argument is never taken", GEN, "                lines.push('{', `    cx->line = ${line};`, `    if (${given}) {`,", "                lines.push('{', `    cx->line = ${line};`, `    if (0 && ${given}) {`,"),
 ("//= is =", GEN, "const given = field.op === '//=' ? `${a} != NULL && !rt_is_undef(cx, *${a})`", "const given = field.op === '//=' ? `${a} != NULL`"),
 ("||= is //=", GEN, ": field.op === '||=' ? `${a} != NULL && rt_is_true(cx, *${a})` : `${a} != NULL`;", ": field.op === '||=' ? `${a} != NULL && !rt_is_undef(cx, *${a})` : `${a} != NULL`;"),
 ("the leaf's fields come first", GEN, "    for (let k = c; k >= 0; k = names.classes[k]!.parent) chain.unshift(names.classes[k]!);", "    for (let k = c; k >= 0; k = names.classes[k]!.parent) chain.push(names.classes[k]!);"),
 ("each class is finished before the next", GEN, "        ...inits.map(l => `    ${l}`),\n        ...chain.flatMap(k => k.adjusts).map(a => `    ${cFn(names, a)}(cx, RT_VOID, 0, NULL, NULL, &f[0]);`),",
  "        ...chain.flatMap((k, j) => [`    ${inits[j]}`, ...k.adjusts.map(a => `    ${cFn(names, a)}(cx, RT_VOID, 0, NULL, NULL, &f[0]);`)]),"),
 ("a class has no parent", GEN, "${info.parent < 0 ? 'rt_undef()' : `f[${names.slots[names.classes[info.parent]!.slot]}]`}", "rt_undef()"),
 ("an array field is a list made once", GEN, "const list = genListWhole([field.default], line, out, c => [`${place} = ${make}_new(cx);`, `${make}_assign(cx, ${place}, ${c});`]);", "const list = genListWhole([field.default], line, out, c => [`${place} = ${c};`]);"),
 ("__CLASS__ is the class written in", GEN, "    case 'curclass': return temp(b, `rt_class_name(cx, ${selfValue(b.names, ownerFn(b))})`);", "    case 'curclass': return { c: 'rt_undef()', place: false };"),
 ("a method's label is its name alone", GEN, "    return m.how === 'adjust' ? `an ADJUST block of ${m.cls}`", "    return m.how === 'adjust' ? s.name"),
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
for src in sorted(glob.glob('t/4[0-3][0-9][0-9]-*.pl') + glob.glob('t/1925-*.pl') + glob.glob('t/3505-*.pl')):
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
    with ThreadPoolExecutor(int(os.environ.get('JOBS', '3'))) as pool:
        return [t[0] for t, ok in zip(which, pool.map(lambda t: passes(t, driver), which)) if not ok]

def unit(tree):
    """How many of the runtime's own tests of classes and objects fail, in the copy."""
    r = subprocess.run(['node', '--test', '--test-name-pattern', "a class dispatches|a constructor's pairs", f'{tree}/runtime/tests/rt.test.ts'], capture_output=True, text=True)
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
    if path in (RT, REF, OBJ, UNWIND, HDR):
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
