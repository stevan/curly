#!/usr/bin/env python3
"""Break step 13d on purpose, one way at a time, in each pass of the
compiler that it touched, and see that a test goes red each time:
references in a string, where perl ends them, what the lexer refuses after
them, the nodes the parser makes of them, how the code generator joins
them, and that a string freezes nothing (D107, D108, D111, D112, D114).

    python3 docs/briefs/step13d-mutations.py            # all of them
    python3 docs/briefs/step13d-mutations.py "braces"   # those named so
    python3 docs/briefs/step13d-mutations.py --match    # only see that each piece of text is there

Nothing in the tree is written: a broken compiler is a copy of bin/,
compiler/src/ and runtime/ under build/mut/tree/. The runtime gained
nothing at 13d, so nothing of it is broken here. Each breakage is run
against every test of step 13d, t/2400*.pl to t/2599*.pl, the refused
ones too, the tests of earlier steps that 13d moved, and the refusals of
strings of 11a and 12b, which go through the code 13d changed, with the knobs
of t/knobs.sh and each test's own `# env:`, as t/run.sh runs them.

A record of step 13d, and not part of make test: each breakage is a piece
of the text as it was then, and one that no longer matches stops the
run."""
import subprocess, glob, sys, os, shutil, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, 't')
import checks

GEN = 'compiler/src/codegen.ts'
RESOLVE = 'compiler/src/resolver.ts'
CHECK = 'compiler/src/checker.ts'
PARSE = 'compiler/src/parser.ts'
LEX = 'compiler/src/lexer.ts'
MUTATIONS = [
 # ---- the lexer: where a chain goes on
 ("no subscript hard after a subscript", LEX, "if (src.startsWith('->[', i) || at() === '[') {", "if (src.startsWith('->[', i)) {"),
 ("no key hard after a subscript", LEX, "} else if (src.startsWith('->{', i) || at() === '{') {", "} else if (src.startsWith('->{', i)) {"),
 # (A third was run, and is taken out: a bracket hard after a variable
 # without an arrow, which an element of the variable's array has taken
 # first, so the line that asked was read by nothing, and went.)
 ("the arrow before an index is left in", LEX, "                if (at() === '-') { take(); take(); }\n                piece = { kind: 'chain', head: piece, index: indexes(false)[0]!, pos: where };", "                if (at() === '-') { take(); }\n                piece = { kind: 'chain', head: piece, index: indexes(false)[0]!, pos: where };"),
 ("a key is an index", LEX, "piece = { kind: 'chain', head: piece, key: key(), pos: where };", "piece = { kind: 'chain', head: piece, index: { kind: 'int', text: '0', negative: false, pos: where }, pos: where }; key();"),
 ("->@* is the last index", LEX, "            take(); take(); take(); take();\n            return { kind: 'deref', head: piece, pos: where };", "            take(); take(); take(); take();\n            return { kind: 'deref', head: piece, last: true, pos: where };"),
 ("->$#* is the whole", LEX, "            return { kind: 'deref', head: piece, last: true, pos: where };\n        }\n        if (src.startsWith('->$*', i)) {", "            return { kind: 'deref', head: piece, pos: where };\n        }\n        if (src.startsWith('->$*', i)) {"),
 ("->$* is not taken", LEX, "        if (src.startsWith('->$*', i)) {\n            take(); take(); take(); take();\n            return { kind: 'sderef', head: piece, pos: where };\n        }\n", ""),
 ("->@[ is not taken", LEX, "        if (src.startsWith('->@[', i)) {", "        if (src.startsWith('->@[!', i)) {"),
 ("a slice through a reference takes one index", LEX, "return { kind: 'dslice', head: piece, indexes: indexes(true), pos: where };", "return { kind: 'dslice', head: piece, indexes: indexes(false), pos: where };"),
 ("->@{ is not refused", LEX, "        if (src.startsWith('->@{', i)) {\n            refuse(", "        if (src.startsWith('->@{!', i)) {\n            refuse("),
 ("->@ and ->$ are text", LEX, "if (src.startsWith('->', i) && (then === '@' || then === '$')) {", "if (src.startsWith('->', i) && then === '%') {"),
 ("nothing refused after a postfix form or braces", LEX, "        if (after !== '') {\n            const what", "        if (after === '!') {\n            const what"),
 ("an arrow after braces is no subscript", LEX, "src.startsWith('->', i) && then !== '' && '[{@$'.includes(then) ? `->${then}` : '';\n        if (after", "'';\n        if (after"),
 ("a postfix form after a whole container is not refused", LEX, "            if (piece.kind === 'deref' || piece.kind === 'sderef' || piece.kind === 'dslice') ends(piece, src.slice(from, i));", ""),
 ("$$ is not cut in a string", LEX, "        if (at() === '$' && (isWordStart(src[i + 1] ?? '') || src[i + 1] === '{')) {\n            const spelled", "        if (at() === '$' && src[i + 1] === '!') {\n            const spelled"),
 ("code in braces is not cut", LEX, "            if (inside === '\\\\' || inside === '[') {", "            if (inside === '!') {"),
 ("no blanks before what the braces hold", LEX, "            let k = i + 1;\n            while (src[k] === ' ') k += 1;", "            const k = i + 1;"),
 ("no blanks after what the braces hold", LEX, "                while (at() === ' ') take();\n                if (at() !== '}') {", "                if (at() !== '}') {"),
 ("a postfix form in the braces", LEX, "                if (head.kind === 'deref' || head.kind === 'sderef' || head.kind === 'dslice') {\n                    refuse(`in a string what stands in ${open}{ ... } is a scalar variable, with subscripts or without (D111): a postfix form there", "                if (head.kind === 'dslice' && head.pos.line < 0) {\n                    refuse(`in a string what stands in ${open}{ ... } is a scalar variable, with subscripts or without (D111): a postfix form there"),
 ("${ } braces are the whole array", LEX, "const piece: Piece = open === '$' ? { kind: 'sderef', head, pos: where } : open === '@'", "const piece: Piece = open === '!' ? { kind: 'sderef', head, pos: where } : open === '@'"),
 ("$#{ } braces are the whole array", LEX, ": open === '@' ? { kind: 'deref', head, pos: where } : { kind: 'deref', head, last: true, pos: where };", ": { kind: 'deref', head, pos: where };"),
 ("$#$ is not cut", LEX, "if (!isWordStart(src[i + 1] ?? '') && src[i + 1] !== '{' && src[i + 1] !== '$') {", "if (!isWordStart(src[i + 1] ?? '') && src[i + 1] !== '{') {"),
 ("anything after a sigil's brace is a name", LEX, "            if (!isWordStart(inside)) {\n                refuse(", "            if (inside === '!') {\n                refuse("),
 ("'::' after an array's element is text", LEX, "        if (piece.kind === 'elem' && src.startsWith('::', i)) refuse(", "        if (piece.kind === 'chain' && src.startsWith('::', i)) refuse("),
 ("'::' after a variable is text", LEX, "            if (src.startsWith('::', i)) refuse(`'::' hard after ${shown} in a string: perl reads a variable of another package; write ${braced}:: or", "            if (src.startsWith(':::', i)) refuse(`'::' hard after ${shown} in a string: perl reads a variable of another package; write ${braced}:: or"),
 ("a key in a string may be anything closed", LEX, "        if (at() !== '}') refuse(KEY, i >= src.length || at() === '\"' ? keyAt : pos());\n        take();\n        const name", "        while (at() !== '}') take();\n        take();\n        const name"),
 ("$_[ in a string is an element", LEX, "        if (name === '_' && (at() === '[' || at() === '{')) refuse(`$_${at()} is an element of perl's own @_ or %_, which are not in the language`, where);", ""),
 # ---- the parser
 ("a chain's key is no key", PARSE, ": p.kind === 'chain' ? (p.key !== undefined ? { kind: 'chain', head: piece(p.head), index: key(p.key, p.pos), hash: true, pos: p.pos }", ": p.kind === 'chain' ? (p.key !== undefined ? { kind: 'chain', head: piece(p.head), index: key(p.key, p.pos), pos: p.pos }"),
 ("a key that is a variable is a word", PARSE, "const key = (k: Key, at: Pos): Expr => (k.kind === 'var' ? { kind: 'var', name: k.name, pos: k.pos } : { kind: 'str', text: k.text, value: k.text, pos: at });", "const key = (k: Key, at: Pos): Expr => (k.kind === 'var' ? { kind: 'str', text: k.name, value: k.name, pos: k.pos } : { kind: 'str', text: k.text, value: k.text, pos: at });"),
 ("a last index through a reference is the count", PARSE, ": p.kind === 'deref' ? (p.last ? { kind: 'deref', head: piece(p.head), last: true, pos: p.pos }", ": p.kind === 'deref' ? (p.last ? { kind: 'deref', head: piece(p.head), pos: p.pos }"),
 ("the scalar through a reference is an element", PARSE, ": p.kind === 'sderef' ? { kind: 'sderef', head: piece(p.head), pos: p.pos }", ": p.kind === 'sderef' ? { kind: 'chain', head: piece(p.head), index: { kind: 'int', text: '0', value: 0n, pos: p.pos }, pos: p.pos }"),
 ("a slice through a reference is the whole", PARSE, ": p.kind === 'dslice' ? { kind: 'slice', name: '', deref: { kind: 'deref', head: piece(p.head), pos: p.pos }, indexes: p.indexes.map(index), pos: p.pos }", ": p.kind === 'dslice' ? { kind: 'deref', head: piece(p.head), pos: p.pos }"),
 ("a chain's head is the variable alone", PARSE, ": { kind: 'chain', head: piece(p.head), index: index(p.index!), pos: p.pos })", ": { kind: 'chain', head: p.head.kind === 'chain' ? piece(p.head.head) : piece(p.head), index: index(p.index!), pos: p.pos })"),
 # ---- the code generator
 ("the whole array in a string is its count", GEN, "const joined = part.kind === 'array' || part.kind === 'slice' || (part.kind === 'deref' && !part.last);", "const joined = part.kind === 'array' || part.kind === 'slice';"),
 # (Nothing in the language can see this one: the last index, joined as a
 # list of one, is the number made a string all the same.)
 ("a last index in a string is joined", GEN, "const joined = part.kind === 'array' || part.kind === 'slice' || (part.kind === 'deref' && !part.last);", "const joined = part.kind === 'array' || part.kind === 'slice' || part.kind === 'deref';"),
 # ---- the resolver: a string in a loop's list freezes nothing
 ("a chain in a string freezes", RESOLVE, "            walk(e.index, declared);\n            if (!quoted) chains.fill(true);", "            walk(e.index, declared);\n            chains.fill(true);"),
 ("a whole container in a string freezes", RESOLVE, "            walk(e.head, declared);\n            if (!quoted) chains.fill(true);\n            return;\n        // Step 13c", "            walk(e.head, declared);\n            chains.fill(true);\n            return;\n        // Step 13c"),
 # ---- the checker: T230's rule through a reference in a string
 ("T230's rule does not see a chain in a string", CHECK, "(r.kind === 'interp' ? r.parts : [r]).forEach(x => variables(x).forEach(v => (v.kind === 'chain' || v.kind === 'sderef' ? ids.add(REACH) : addId(w, ids, w.names.of.get(v)!))));\n                if (r.kind === 'interp') r.parts.forEach(x => reads(x, names));", "(r.kind === 'interp' ? [] : [r]).forEach(x => variables(x).forEach(v => (v.kind === 'chain' || v.kind === 'sderef' ? ids.add(REACH) : addId(w, ids, w.names.of.get(v)!))));"),
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
MOVED = '13[5-9][0-9]|14[0-5][0-9]|17[2-6][0-9]|196[0-3]|2635|383[3-5]'
for src in sorted(glob.glob('t/2[45][0-9][0-9]-*.pl') + [p for p in glob.glob('t/*.pl') if re.match(rf't/({MOVED})-', p)]):
    head = open(src, encoding='utf-8', errors='replace').read(1200)
    env = dict(os.environ)
    env.update(knobs)
    found = re.search(r'^# env: (.*)$', head, re.M)
    if found:
        env.update(pair.split('=', 1) for pair in found.group(1).split())
    tests.append((os.path.basename(src)[:-3], open(src[:-3] + '.expected', 'rb').read(), env, 'kind: refused' in head))

def passes(test, driver):
    name, expected, env, refused = test
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
    with ThreadPoolExecutor(4) as pool:
        return [t[0] for t, ok in zip(tests, pool.map(lambda t: passes(t, driver), tests)) if not ok]

def copy():
    shutil.rmtree('build/mut/tree', ignore_errors=True)
    for part in ('bin', 'compiler/src', 'runtime'):
        shutil.copytree(part, 'build/mut/tree/' + part)

os.makedirs('build/mut', exist_ok=True)
# The driver of a broken compiler links a runtime built once (CURLY_RT_OBJ).
os.environ['CURLY_RT_OBJ'] = os.path.abspath('build/mut/rt-driver.o')
if os.path.exists(os.environ['CURLY_RT_OBJ']):
    os.remove(os.environ['CURLY_RT_OBJ'])
copy()
whole = golden('build/mut/tree/bin/curlyc.ts')
assert whole == [], f'things as they are fail: {whole}'
print(f'{len(tests)} golden tests pass as things are', flush=True)
missed = []
for name, path, old, new in MUTATIONS:
    if only and not any(o in name for o in only):
        continue
    copy()
    text = open(path).read()
    assert text.count(old) == 1, (name, text.count(old))
    open('build/mut/tree/' + path, 'w').write(text.replace(old, new))
    failed = golden('build/mut/tree/bin/curlyc.ts')
    if failed:
        print(f'{name}: golden {len(failed)} ({", ".join(f[:4] for f in failed[:6])})', flush=True)
    else:
        print(f'{name}: golden 0   <-- NOT CAUGHT', flush=True)
        missed.append(name)
print(f'{len(missed)} not caught: {missed}')
