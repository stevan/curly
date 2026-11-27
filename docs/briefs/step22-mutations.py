#!/usr/bin/env python3
"""Break step 22 on purpose, one way at a time, in the runtime and in each
pass of the compiler, and see that a test goes red each time: the numeric
builtins (22a), the bit operators (22b), rand, srand and time (22c).

    python3 docs/briefs/step22-mutations.py            # all of them
    python3 docs/briefs/step22-mutations.py "srand"    # those named so
    python3 docs/briefs/step22-mutations.py --match    # only see that each piece of text is there

Nothing in the tree is written: a broken runtime or compiler is a copy of
bin/, compiler/src/ and runtime/ under build/mut22/tree/. Each breakage is
caught if a golden test of step 22, t/4400*.pl to t/4699*.pl, the refused
ones too, goes red, run with the knobs of t/knobs.sh and each test's own
`# env:`, as t/run.sh runs them.

A record of step 22, and not part of make test: each breakage is a piece
of the text as it was then, and one that no longer matches stops the
run."""
import subprocess, glob, sys, os, shutil, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, 't')
import checks

NUM = 'runtime/num.c'
RT = 'runtime/rt.c'
GEN = 'compiler/src/codegen.ts'
CHECK = 'compiler/src/checker.ts'
PARSE = 'compiler/src/parser.ts'
LEX = 'compiler/src/lexer.ts'
NAMES = 'compiler/src/names.ts'
C_FILES = (NUM, RT)
OUT = 'build/mut22'
MUTATIONS = [
 # ---- 22a, the runtime
 ("int of an Int is 0", NUM, "    if (x.is_int) return rt_int(x.i);\n    double d = x.n;", "    if (x.is_int) return rt_int(0);\n    double d = x.n;"),
 ("int of a Num past 2^63 is taken", NUM, "    if (d >= TWO_63 && d < 2 * TWO_63) rt_fault(", "    if (0) rt_fault("),
 ("int of -2^63 is an Int", NUM, "    if (d > -TWO_63 && d < TWO_63) return rt_int((int64_t)trunc(d));", "    if (d >= -TWO_63 && d < TWO_63) return rt_int((int64_t)trunc(d));"),
 ("int of a Num keeps the Num", NUM, "    if (d > -TWO_63 && d < TWO_63) return rt_int((int64_t)trunc(d));", "    if (d > -TWO_63 && d < TWO_63) return rt_num(trunc(d));"),
 ("int rounds", NUM, "return rt_int((int64_t)trunc(d));", "return rt_int((int64_t)round(d));"),
 ("abs of -2^63 is taken", NUM, "        if (x.i == INT64_MIN) rt_fault(", "        if (0) rt_fault("),
 ("abs of a negative Int is itself", NUM, "        return rt_int(x.i < 0 ? -x.i : x.i);", "        return rt_int(x.i);"),
 ("abs of a point string is an Int", NUM, "    if (!x.soft && integral(x, &w))", "    if (integral(x, &w))"),
 ("abs of an integral Num is a Num", NUM, "    if (!x.soft && integral(x, &w)) return rt_int(w < 0 ? -w : w);", "    if (0) return rt_int(w < 0 ? -w : w);"),
 ("abs of a Num is the Num", NUM, "    return rt_num(fabs(x.n));", "    return rt_num(x.n);"),
 ("a minus-zero string is taken", NUM, "    if (v.tag == RT_TAG_STR && negative_zero(cx, v, d)) {", "    if (0) {"),
 ("sqrt below zero is taken", NUM, "    if (d < 0.0) rt_fault(cx, \"sqrt of a number below zero\");", ""),
 ("sqrt of zero faults", NUM, "    if (d < 0.0) rt_fault(cx, \"sqrt of a number below zero\");", "    if (d <= 0.0) rt_fault(cx, \"sqrt of a number below zero\");"),
 ("log of zero is taken", NUM, "    if (d <= 0.0) rt_fault(cx, \"log of zero or a number below zero\");", "    if (d < 0.0) rt_fault(cx, \"log of zero or a number below zero\");"),
 ("errno is not noted", NUM, "    if (err != 0 || (r != 0.0 && fpclassify(r) == FP_SUBNORMAL) || (r == 0.0 && vanished)) cx->underflowed = 1;", "    if ((r != 0.0 && fpclassify(r) == FP_SUBNORMAL) || (r == 0.0 && vanished)) cx->underflowed = 1;"),
 ("an underflow is not noted", NUM, "    if (err != 0 || (r != 0.0 && fpclassify(r) == FP_SUBNORMAL) || (r == 0.0 && vanished)) cx->underflowed = 1;", ""),
 ("an infinity is a Num", NUM, "    return num(cx, r);\n}\n\nrt_value rt_num_sqrt", "    return rt_num(r);\n}\n\nrt_value rt_num_sqrt"),
 ("exp is sin", NUM, "    double r = exp(d);", "    double r = sin(d);"),
 ("cos is sin", NUM, "    double r = cos(d);", "    double r = sin(d);"),
 ("log is log10", NUM, "    double r = log(d);", "    double r = log10(d);"),
 ("atan2 takes its arguments the other way", NUM, "    double r = atan2(p, q);", "    double r = atan2(q, p);"),
 ("atan2 takes a negative zero", NUM, "    if ((p == 0.0 && signbit(p)) || (q == 0.0 && signbit(q))) {", "    if (0) {"),
 ("atan2 takes a negative zero for x", NUM, "    if ((p == 0.0 && signbit(p)) || (q == 0.0 && signbit(q))) {", "    if ((p == 0.0 && signbit(p))) {"),
 ("hex takes no 0x", NUM, "    if (end - p >= 2 && p[0] == '0' && (p[1] == 'x' || p[1] == 'X')) p += 2;", "    if (0) p += 2;"),
 ("a comparison under & is taken", PARSE, "                    if (side.kind === 'binary' && !side.bracketed && NUMERIC_COMPARISONS.has(side.op)) {", "                    if (false) {"),
 ("a comparison on the left of & is taken", PARSE, "                for (const side of [left, right]) {", "                for (const side of [right]) {"),
 ("hex takes no x alone", NUM, "    else if (p < end && (*p == 'x' || *p == 'X')) p += 1;", ""),
 ("hex takes two underscores", NUM, "            if (after_underscore || p + 1 == end) return -1;", "            if (p + 1 == end) return -1;"),
 ("hex takes an underscore last", NUM, "            if (after_underscore || p + 1 == end) return -1;", "            if (after_underscore) return -1;"),
 ("an underscore first is refused", NUM, "    if (p < end && *p == '_') {\n        p++;", "    if (p < end && *p == '_') {\n        return -1;"),
 ("past 32 bits is taken", NUM, "        if (v > 0xFFFFFFFFu) return -2;", "        if (v > 0xFFFFFFFFFFFFu) return -2;"),
 ("a digit past the base is taken", NUM, "        if (d >= base) return -1;", "        if (d >= 16) return -1;"),
 ("oct takes no blanks first", NUM, "    while (p < end && blank(*p)) p++;\n    int base = 8;", "    int base = 8;"),
 ("oct has no binary", NUM, "    else if (c == 'b' || c == 'B') base = 2;", ""),
 ("oct's 0o is octal's 0", NUM, "    if (c == 'x' || c == 'X' || c == 'b' || c == 'B' || c == 'o' || c == 'O') p = q + 1;", "    if (c == 'x' || c == 'X' || c == 'b' || c == 'B') p = q + 1;"),
 # ---- 22b, the runtime
 ("an answer past 2^63 is taken", NUM, "    if (u > (uint64_t)INT64_MAX) rt_fault(", "    if (0) rt_fault("),
 ("an answer of 2^63 is taken", NUM, "    if (u > (uint64_t)INT64_MAX) rt_fault(", "    if (u > (uint64_t)INT64_MAX + 1) rt_fault("),
 ("& is |", NUM, "    return unsigned_answer(cx, x & y);", "    return unsigned_answer(cx, x | y);"),
 ("^ is |", NUM, "    return unsigned_answer(cx, x ^ y);", "    return unsigned_answer(cx, x | y);"),
 ("|= of undef faults", NUM, "    return rt_bit_or(cx, a.tag == RT_TAG_UNDEF ? rt_int(0) : a, b);", "    return rt_bit_or(cx, a, b);"),
 ("^= of undef faults", NUM, "    return rt_bit_xor(cx, a.tag == RT_TAG_UNDEF ? rt_int(0) : a, b);", "    return rt_bit_xor(cx, a, b);"),
 ("~ is the minus", NUM, "    return unsigned_answer(cx, ~bits_of(cx, a));", "    return unsigned_answer(cx, -bits_of(cx, a));"),
 ("a negative count shifts the same way", NUM, "        left = !left;\n", ""),
 ("a count of 64 is C's", NUM, "    if (count >= 64) return 0;", "    if (count >= 65) return 0;"),
 ("an operand is not cut by substr's rule", NUM, "    return (uint64_t)whole_of(cx, v);", "    return (uint64_t)(int64_t)as_double(numeric(cx, v));"),
 ("<< is >>", NUM, "    return unsigned_answer(cx, shifted(x, n, 1));", "    return unsigned_answer(cx, shifted(x, n, 0));"),
 # ---- 22c, the runtime
 ("the generator's multiplier is another", NUM, "UINT64_C(0x5DEECE66D)", "UINT64_C(0x5DEECE66F)"),
 ("the state is not 48 bits", NUM, "& UINT64_C(0xFFFFFFFFFFFF);", "& UINT64_C(0xFFFFFFFFFFFFF);"),
 ("the seed is not shifted", NUM, "    cx->rand_state = UINT64_C(0x330E) + ((uint64_t)seed << 16);", "    cx->rand_state = UINT64_C(0x330E) + (uint64_t)seed;"),
 ("the seed is 64 bits", NUM, "    seed_with(cx, (uint32_t)(uint64_t)n);", "    cx->rand_state = UINT64_C(0x330E) + ((uint64_t)n << 16); cx->rand_seeded = 1;"),
 ("rand(0) is 0", NUM, "    if (v == 0.0) v = 1.0;\n", ""),
 ("srand of 0 is 0", NUM, "    return n == 0 ? rt_string(&ZERO_BUT_TRUE) : rt_int(n);", "    return rt_int(n);"),
 ("srand of a negative is taken", NUM, "        if (v.as.i < 0) rt_fault(cx, why);", ""),
 ("srand of a fraction is taken", NUM, "        if (!(d >= 0.0 && d < 1e15 && d == trunc(d))) rt_fault(cx, why);", "        if (!(d >= 0.0 && d < 1e15)) rt_fault(cx, why);"),
 ("srand of a string with a blank is taken", NUM, "            if (!digit(c)) rt_fault(cx, why);", "            if (!digit(c)) continue;"),
 ("srand of a boolean is taken", NUM, "    if (v.tag == RT_TAG_BOOL) rt_fault(cx, why);", "    if (v.tag == RT_TAG_BOOL) return seeded(cx, v.as.i);"),
 ("rand seeds itself every time", NUM, "    if (!cx->rand_seeded) seed_with(cx, any_seed());", "    seed_with(cx, any_seed());"),
 ("the clock is not virtual", NUM, "    if (cx->clock != 0) return rt_int((int64_t)cx->clock);", ""),
 ("the knob is not read", RT, "    cx.clock = knob(\"CURLY_TIME\", (uint64_t)INT64_MAX);", ""),
 # ---- the compiler
 ("int is abs", NAMES, "    ['int', { kind: 'unary', rt: 'rt_num_int' }],", "    ['int', { kind: 'unary', rt: 'rt_num_abs' }],"),
 ("~ is not in", NAMES, "live('~', 'rt_bit_not'), ...ops('~.', '\\\\'),", "...ops('~', '~.', '\\\\'),"),
 ("<< binds as + does", NAMES, "    { assoc: 'left', infix: [live('<<', 'rt_shl'), live('>>', 'rt_shr')] },", "    { assoc: 'left', infix: [] },"),
 ("|= is |", NAMES, "put('|=', 'rt_bit_or_to')", "put('|=', 'rt_bit_or')"),
 ("&= is not in", NAMES, "        put('&=', 'rt_bit_and'), ", "        ...ops('&='), "),
 ("rand takes no bare form", NAMES, "    ['rand', { kind: 'unary', rt: 'rt_rand', bare: 'rt_rand0', effect: true, volatile: true }],", "    ['rand', { kind: 'unary', rt: 'rt_rand', effect: true, volatile: true }],"),
 ("rand folds", NAMES, "    ['rand', { kind: 'unary', rt: 'rt_rand', bare: 'rt_rand0', effect: true, volatile: true }],", "    ['rand', { kind: 'unary', rt: 'rt_rand', bare: 'rt_rand0', effect: true }],"),
 ("srand is no statement", NAMES, "    ['srand', { kind: 'unary', rt: 'rt_srand', bare: 'rt_srand0', effect: true, volatile: true }],", "    ['srand', { kind: 'unary', rt: 'rt_srand', bare: 'rt_srand0', volatile: true }],"),
 ("the string bitwise operators are not named cut", LEX, "            if (STRINGWISE.has(op)) refuse(", "            if (false) refuse("),
 ("rand before * is taken", PARSE, "            if (name.bare !== undefined && (open.kind === 'op' || open.kind === 'word') && infixOp(open.text) && !prefixOp(open.text)) {", "            if (false) {"),
 ("rand before == is refused", PARSE, "const AFTER_BARE = new Set(['==', '!=', '>', '>=', '|', '^', '&&', '||', '>>']);", "const AFTER_BARE = new Set(['!=']);"),
 ("time takes an argument", PARSE, "                if (peek().kind !== ')') refuse(`${head.text} takes no argument`, peek().pos);\n                next();", "                if (peek().kind !== ')') { expression(COMMA_ROW + 1); }\n                next();"),
 ("time is no value word", LEX, " || NAMES.get(last.text)?.kind === 'term'));", "));"),
 ("~ after say $x is taken", LEX, "                    || a === '~'\n", ""),
 ("<< after say $x is taken", LEX, "                    || (a === '<' && b === '<' && c !== '' && !isBlank(c) && c !== '=')", ""),
 ("rand and srand fold", CHECK, "    : e.kind === 'apply' && isVolatile(e.name) ? false\n", ""),
 ("rand(...) is no statement", CHECK, "            || (s.expr.kind === 'apply' && isEffect(s.expr.name));", ";"),
 ("the bare form calls the one with an argument", GEN, "    const rt = name?.kind === 'unary' ? (e.args.length === 0 ? name.bare : name.rt)", "    const rt = name?.kind === 'unary' ? name.rt"),
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
for src in sorted(glob.glob('t/4[456][0-9][0-9]-*.pl')):
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
        if subprocess.run(['cc', '-o', f'{OUT}/{name}', f'{OUT}/{name}.o', f'{OUT}/rt.o', '-lm'], capture_output=True).returncode:
            return False
    else:
        built = subprocess.run(['node', driver, '-o', f'{OUT}/{name}', f't/{name}.pl'], capture_output=True, env=dict(os.environ, CURLY_RT_OBJ=os.path.abspath(f'{OUT}/rt-good.o')))
        if refused:
            return built.stderr + f'exit: {built.returncode}\n'.encode() == expected
        if built.returncode:
            return False
    try:
        run = checks.run_capped(['sh', '-c', 'exec "$0" 2>&1', f'{OUT}/{name}'], env, b'', 20)
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

def copy():
    shutil.rmtree(f'{OUT}/tree', ignore_errors=True)
    for part in ('bin', 'compiler/src', 'runtime'):
        shutil.copytree(part, f'{OUT}/tree/' + part)

def runtime():
    """The copy's runtime, compiled; whether it compiled."""
    return subprocess.run(['cc', '-O1', '-c', f'-I{OUT}/tree/runtime', '-o', f'{OUT}/rt.o', f'{OUT}/tree/runtime/rt.c'], capture_output=True).returncode == 0

os.makedirs(OUT, exist_ok=True)
copy()
subprocess.run(['cc', '-O1', '-c', '-Iruntime', '-o', f'{OUT}/rt-good.o', 'runtime/rt.c'], check=True)
whole = golden(f'{OUT}/tree/bin/curlyc.ts')
assert whole == [], f'things as they are fail: {whole}'
for name, _, _, _ in ran:
    subprocess.run(['cc', '-O0', '-c', '-Iruntime', '-o', f'{OUT}/{name}.o', f'{OUT}/{name}.c'], check=True)
assert runtime() and golden(None) == []
print(f'{len(tests)} golden tests pass as things are', flush=True)
missed = []
for name, path, old, new in MUTATIONS:
    if only and not any(o in name for o in only):
        continue
    copy()
    text = open(path).read()
    assert text.count(old) == 1, (name, text.count(old))
    open(f'{OUT}/tree/' + path, 'w').write(text.replace(old, new))
    if path in C_FILES:
        failed = golden(None) if runtime() else ['the runtime does not compile']
    else:
        failed = golden(f'{OUT}/tree/bin/curlyc.ts')
    if failed:
        print(f'{name}: golden {len(failed)} ({", ".join(f[:4] for f in failed[:6])})', flush=True)
    else:
        print(f'{name}: golden 0   <-- NOT CAUGHT', flush=True)
        missed.append(name)
print(f'{len(missed)} not caught: {missed}')
