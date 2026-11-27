#!/usr/bin/env python3
"""Break step 13c on purpose, one way at a time, in the runtime and in each
pass of the compiler, and see that a test goes red each time: references to
scalars, the cell a taken variable lives in, the scalar through a
reference read and stored to, what a store makes, and the walks over names
that know what references reach and the scalars among it (D107 to D110,
D112, D114).

    python3 docs/briefs/step13c-mutations.py            # all of them
    python3 docs/briefs/step13c-mutations.py "cell"     # those named so
    python3 docs/briefs/step13c-mutations.py --match    # only see that each piece of text is there

Nothing in the tree is written: a broken runtime or compiler is a copy of
bin/, compiler/src/ and runtime/ under build/mut/tree/. Each breakage is
run two ways, and is caught if either goes red:

  golden   every test of step 13c, t/2200*.pl to t/2399*.pl, the refused
           ones too, and 1914, 1924 and 1928, run with the knobs of t/knobs.sh
           and each test's own `# env:`, as t/run.sh runs them
  unit     the runtime's own tests of references, in the copy

A record of step 13c, and not part of make test: each breakage is a piece
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
UNWIND = 'runtime/unwind.c'
MUTATIONS = [
 # ---- the runtime
 ("a cell is an array", REF, "    c.tag = RT_TAG_CELL;\n    *slot = c;", "    *slot = c;"),
 ("a cell is made empty", REF, "    rt_value c = rt_array_new(cx);\n    append(cx, c.as.a, *slot);", "    rt_value c = rt_array_new(cx);\n    append(cx, c.as.a, rt_undef());"),
 ("a reference to a scalar is one to an array", REF, "    v.tag = RT_TAG_SREF;\n    v.as.a = cell.as.a;", "    v.tag = RT_TAG_AREF;\n    v.as.a = cell.as.a;"),
 ("the scalar through a reference is read through an array's", REF, "    return hash == 2 ? RT_TAG_SREF : hash ? RT_TAG_HREF : RT_TAG_AREF;", "    return hash ? RT_TAG_HREF : RT_TAG_AREF;"),
 ("what it reads through is an array", REF, "    v.tag = hash == 2 ? RT_TAG_CELL : hash ? RT_TAG_HASH : RT_TAG_ARRAY;", "    v.tag = hash ? RT_TAG_HASH : RT_TAG_ARRAY;"),
 ("the wrong reference says array", REF, "        rt_fault(cx, hash == 2 ? NOT_SCALAR : hash ? NOT_HASH : NOT_ARRAY);", "        rt_fault(cx, hash ? NOT_HASH : NOT_ARRAY);"),
 ("a scalar made holds nothing", REF, "    rt_value c = rt_array_new(cx);\n    append(cx, c.as.a, rt_undef());\n    c.tag = RT_TAG_CELL;\n    return c;", "    rt_value c = rt_array_new(cx);\n    c.tag = RT_TAG_CELL;\n    return c;"),
 ("a scalar made is an array", REF, "    if (hash != 2) return hash ? rt_hash_new(cx) : rt_array_new(cx);", "    if (hash != 3) return hash ? rt_hash_new(cx) : rt_array_new(cx);"),
 ("a made scalar's reference is an array's", REF, "    v.tag = c.tag == RT_TAG_CELL ? RT_TAG_SREF : c.tag == RT_TAG_HASH ? RT_TAG_HREF : RT_TAG_AREF;", "    v.tag = c.tag == RT_TAG_HASH ? RT_TAG_HREF : RT_TAG_AREF;"),
 ("ref of a reference to a scalar is empty", REF, "    if (v.tag == RT_TAG_SREF) return rt_string(is_ref(RT_CELL(v)) ? &STR_REF : &STR_SCALAR);\n", ""),
 ("ref never says REF", REF, "is_ref(RT_CELL(v)) ? &STR_REF : &STR_SCALAR", "&STR_SCALAR"),
 ("the collector does not walk a cell", RT, "case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_CELL: case RT_TAG_SREF:\n        mark_container", "case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_SREF:\n        mark_container"),
 ("the collector does not follow a reference to a scalar", RT, "case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_CELL: case RT_TAG_SREF:\n        mark_container", "case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_CELL:\n        mark_container"),
 ("a reference to a scalar is a string", RT, "    if (v.tag == RT_TAG_AREF || v.tag == RT_TAG_HREF || v.tag == RT_TAG_SREF) rt_fault(cx, \"a reference where a string is wanted\");", "    if (v.tag == RT_TAG_AREF || v.tag == RT_TAG_HREF) rt_fault(cx, \"a reference where a string is wanted\");"),
 ("a reference to a scalar is a number", RT, "    case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_SREF:\n        rt_fault(cx, \"a reference where a number is wanted\");", "    case RT_TAG_AREF: case RT_TAG_HREF:\n        rt_fault(cx, \"a reference where a number is wanted\");"),
 ("a reference to a scalar is false", RT, "    case RT_TAG_AREF: case RT_TAG_HREF: case RT_TAG_SREF: return 1;", "    case RT_TAG_AREF: case RT_TAG_HREF: return 1;"),
 ("a reference to a scalar is no value", RT, "|| tag == RT_TAG_AREF || tag == RT_TAG_HREF || tag == RT_TAG_SREF;", "|| tag == RT_TAG_AREF || tag == RT_TAG_HREF;"),
 ("two references to a scalar are compared as numbers", RT, "    return v.tag == RT_TAG_AREF || v.tag == RT_TAG_HREF || v.tag == RT_TAG_SREF;", "    return v.tag == RT_TAG_AREF || v.tag == RT_TAG_HREF;"),
 ("a reference to a scalar is printed", RT, "v.tag == RT_TAG_UNDEF || v.tag == RT_TAG_AREF || v.tag == RT_TAG_HREF || v.tag == RT_TAG_SREF) {", "v.tag == RT_TAG_UNDEF || v.tag == RT_TAG_AREF || v.tag == RT_TAG_HREF) {"),
 ("a reference to a scalar thrown is a message", UNWIND, "a->items[0].tag == RT_TAG_HREF || a->items[0].tag == RT_TAG_SREF)) rt_throw", "a->items[0].tag == RT_TAG_HREF)) rt_throw"),
 # ---- the lexer
 ("${ is a name in braces", LEX, "            if (at() === '{') {\n                cast('$', start);\n                continue;\n            }", "            if (at() === '{') refuse('${', start);"),
 ("->$* is refused", LEX, "const whole = two === '@*' || two === '%*' || two === '$*' ? two :", "const whole = two === '@*' || two === '%*' ? two :"),
 ("->$* ends no value", LEX, "const WHOLE = new Set(['->@*', '->%*', '->$#*', '->$*']);", "const WHOLE = new Set(['->@*', '->%*', '->$#*']);"),
 ("a step after ->$* ends no value", LEX, "                || (target?.kind === 'op' && target.text === '->$*');", ";"),
 ("an arrow after ${ } is taken", LEX, "                    if (src.startsWith('->', after) && opened === 'sderef') refuse(", "                    if (false) refuse("),
 ("an arrow after ->$* is a subscript's", LEX, "                    if (whole === '$*' && src.startsWith('->', after)) refuse(", "                    if (false) refuse("),
 ("three dollars are a name", LEX, " || src[i + 1] === '{' || src[i + 1] === '$')) {", " || src[i + 1] === '{')) {"),
 ("the braces of ${ } are the whole container's", LEX, "        braces.push(sigil === '$' ? 'sderef' : 'deref');", "        braces.push('deref');"),
 # ---- the parser
 ("->$* makes nothing of its head", PARSE, "                return { kind: 'sderef', head: e, pos: e.pos };", "                return e;"),
 ("${ } is the whole array", PARSE, "            if (t.text === '$') return stepAfter({ kind: 'sderef', head, pos: t.pos });\n", ""),
 ("no step after the scalar through a reference", PARSE, "target.kind !== 'chain' && target.kind !== 'sderef')) return target;", "target.kind !== 'chain')) return target;"),
 ("++${ } is refused", PARSE, "            if (v.kind === 'cast' && v.text === '$') {", "            if (false) {"),
 ("\\$r->$* is taken", PARSE, "            if ((what.kind === 'var' && after.kind === 'op' && after.text === '->$*') || (what.kind === 'cast' && what.text === '$')) {", "            if (false) {"),
 ("\\$x is refused", PARSE, "            if (what.kind === 'var') return { kind: 'ref', of: { kind: 'var', name: what.name, pos: what.pos }, pos: t.pos };", "            if (what.kind === 'var') return refuse('no', t.pos);"),
 ("the scalar through a reference is not assigned", PARSE, "left.kind !== 'chain' && left.kind !== 'sderef') {", "left.kind !== 'chain') {"),
 ("the scalar through a reference is no list assignment's target", PARSE, "left.kind === 'chain' || left.kind === 'sderef' || left.kind === 'array'", "left.kind === 'chain' || left.kind === 'array'"),
 # ---- the resolver
 ("a reference to a loop's variable is taken", RESOLVE, "            if (e.of.kind === 'var' && readonly.has(id)) {", "            if (false) {"),
 ("a scalar's reference taken leaves it in its slot", RESOLVE, "            taken.add(id);\n            return;\n        }", "            if (e.of.kind === 'array') taken.add(id);\n            return;\n        }"),
 # ---- the checker
 ("the scalar through a reference names nothing", CHECK, "    else if (e.kind === 'deref' || e.kind === 'sderef') whole(e);", "    else if (e.kind === 'deref') whole(e);"),
 ("a store to the scalar through a reference names nothing", CHECK, "    else if ((e.kind === 'assign' || (e.kind === 'step' && e.before)) && e.target.kind === 'sderef') whole(e.target);\n", ""),
 ("a store through a scalar reference changes nothing", CHECK, "e.target.kind === 'sderef') return direct ? [] : [REACH, CELLS, ...making(w, e.target)];", "e.target.kind === 'sderef') return [];"),
 ("a store through a scalar reference changes no scalar", CHECK, "e.target.kind === 'sderef') return direct ? [] : [REACH, CELLS, ...making(w, e.target)];", "e.target.kind === 'sderef') return direct ? [] : [REACH, ...making(w, e.target)];"),
 ("a list assignment through a scalar reference changes nothing", CHECK, "            : t.kind === 'sderef' ? (direct ? [] : [REACH, CELLS, ...making(w, t)])", "            : t.kind === 'sderef' ? []"),
 ("a taken scalar is not what references reach", CHECK, "const addId = (w: World, into: Set<number>, id: number): void => {\n    into.add(id);\n    if (w.names.taken.has(id)) into.add(REACH);", "const addId = (w: World, into: Set<number>, id: number): void => {\n    into.add(id);\n    if (w.names.taken.has(id) && w.names.isArray[id]) into.add(REACH);"),
 ("a loop over the scalar through a reference guards nothing", CHECK, "        if (e.kind === 'sderef') scalars.set(CELLS, e);\n", ""),
 ("a loop over a taken scalar guards it by name only", CHECK, "        if (e.kind === 'var' && w.names.taken.has(w.names.of.get(e)!)) scalars.set(CELLS, e);\n", ""),
 ("a store by name in the loop is no scalar's", CHECK, "            if (scalars.has(CELLS) && w.names.taken.has(id) && !w.names.isArray[id]) refused(CELLS, e);\n", ""),
 ("a sub's store to a file's taken scalar is no scalar's", CHECK, "            if (names.taken.has(id) && !names.isArray[id] && !own_) own[fn]!.add(CELLS);\n", ""),
 ("a sub's store to a file's taken scalar reaches nothing", CHECK, "            if (names.taken.has(id) && !own_) own[fn]!.add(REACH);\n", ""),
 ("the scalar through a reference is read early, unnamed in a row", CHECK, "        variables(piece).forEach(v => (v.kind === 'chain' || v.kind === 'sderef' ? readIds.add(REACH)", "        variables(piece).forEach(v => (v.kind === 'chain' || v.kind === 'sderef' ? readIds.add(-9)"),
 ("the scalar through a reference is no place a value is", CHECK, "    else if (e.kind === 'chain' || e.kind === 'sderef') into.add(REACH);", "    else if (e.kind === 'chain') into.add(REACH);"),
 ("making the scalar is not checked against the right side", CHECK, "            if (t.kind === 'chain' || t.kind === 'deref' || t.kind === 'sderef') checkMaking(w, t, e.value, true);", "            if (t.kind === 'chain' || t.kind === 'deref') checkMaking(w, t, e.value, true);"),
 ("T230's rule does not look through the scalar", CHECK, "        const index = e.target.kind === 'chain' ? chainParts(e.target) : e.target.kind === 'sderef' ? derefParts(e.target) : [e.target.index];", "        const index = e.target.kind === 'chain' ? chainParts(e.target) : e.target.kind === 'sderef' ? [] : [e.target.index];"),
 ("the scalar is no target of a list assignment", CHECK, "t.kind === 'chain' || t.kind === 'sderef' || array ||", "t.kind === 'chain' || array ||"),
 ("the head in the braces is not checked", CHECK, "    case 'sderef': return [[e.head, 'scalar']];", "    case 'sderef': return [];"),
 # (Two more were run, and are taken out: the resolver's `chains.fill` for
 # the scalar through a reference, and `addId`'s adding the scalars
 # references reach, each a line nothing read. Both lines went.)
 # ---- the code generator
 ("a taken variable is its slot", GEN, "    return id !== undefined && inCell(b.names, id) ? `RT_CELL(${slotOf(b, e)})` : slotOf(b, e);", "    return slotOf(b, e);"),
 ("a my reached again keeps its cell", GEN, "        if (!isFile(b, e)) b.vars.push(`${slotOf(b, e)} = rt_undef(); // my $${e.name}`, ...(inCell(b.names, b.names.of.get(e)!) ? [`rt_cell_wrap(cx, &${slotOf(b, e)});`] : []));",
  "        if (!isFile(b, e)) b.vars.push(...(inCell(b.names, b.names.of.get(e)!) ? [`if (${slotOf(b, e)}.tag != RT_TAG_CELL) { ${slotOf(b, e)} = rt_undef(); rt_cell_wrap(cx, &${slotOf(b, e)}); } else RT_CELL(${slotOf(b, e)}) = rt_undef();`] : [`${slotOf(b, e)} = rt_undef(); // my $${e.name}`]));"),
 ("a file's taken variable has no cell from the start", GEN, "                ...(inCell(names, id) ? [`    rt_cell_wrap(cx, &f[${names.slots[id]}]);`] : [])] : [])),", "                ] : [])),"),
 ("a taken parameter has no cell", GEN, "        const cell = p.my !== undefined && inCell(names, names.of.get(p.my)!) ? [`rt_cell_wrap(cx, &${slot});`] : [];", "        const cell: string[] = [];"),
 ("a taken catch variable has no cell", GEN, "...(inCell(out.names, id) ? [`rt_cell_wrap(cx, &${v});`] : []), '{', ...indent(handler), '}']),", "'{', ...indent(handler), '}']),"),
 ("the scalar through a reference is never made", GEN, "    return genChain(whole, b, store, true).container;", "    return genChain(whole, b, false, true).container;"),
 ("the cell is kept for a freeze", GEN, "        if (b.frozen !== undefined && kind(k) !== 2) b.lines.push(", "        if (b.frozen !== undefined) b.lines.push("),
 ("a chain's last link is not the scalar", GEN, "    const kind = (k: number): number => (scalar && k === subs.length - 1 ? 2 : subs[k]!.hash ? 1 : 0);", "    const kind = (k: number): number => (scalar && k === subs.length ? 2 : subs[k]!.hash ? 1 : 0);"),
 ("= makes the scalar before the right side", GEN, "                const value = genExpr(e.value, b);\n                const cell = genCell(target, b, true);", "                const cell = genCell(target, b, true);\n                const value = genExpr(e.value, b);"),
 ("an assigning operator reads through, and makes nothing", GEN, "            const cell = genCell(target, b, true);\n            if (op.when !== undefined) {", "            const cell = genCell(target, b, false);\n            if (op.when !== undefined) {"),
 ("||= through a reference always stores", GEN, "                b.lines.push(`if (${op.when}(cx, RT_CELL(${cell}))) {`);", "                b.lines.push(`if (1) {`);"),
 ("$$r++ is worth what it holds after", GEN, "            return e.before ? now : was;\n        }\n        const v = variable(b, e.target);", "            return now;\n        }\n        const v = variable(b, e.target);"),
 ("a list assignment through the scalar is not made", GEN, "            if (t.kind === 'sderef') containers[n] = genCell(t, b, true);", "            if (t.kind === 'sderef') containers[n] = genCell(t, b, false);"),
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
for src in sorted(glob.glob('t/2[23][0-9][0-9]-*.pl') + glob.glob('t/1914-*.pl') + glob.glob('t/1924-*.pl') + glob.glob('t/1928-*.pl')):
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
    r = subprocess.run(['node', '--test', '--test-name-pattern', 'reference|arrow|hop|walks a chain|cell', f'{tree}/runtime/tests/rt.test.ts'], capture_output=True, text=True)
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
    if path in (RT, REF, HASH, UNWIND):
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
