#!/usr/bin/env python3
"""Break step 19 on purpose, one way at a time, in the runtime's matcher
and in each pass of the compiler, and see that a test goes red each time.

    python3 docs/briefs/step19-mutations.py            # all of them
    python3 docs/briefs/step19-mutations.py "lazy"     # those named so
    python3 docs/briefs/step19-mutations.py --match    # only see that each piece of text is there

Nothing in the tree is written: a broken runtime or compiler is a copy of
bin/, compiler/src/ and runtime/ under build/mut/tree/. Each breakage is
run two ways, and is caught if either goes red:

  golden   every test of step 19, t/5100*.pl to t/5699*.pl, the refused
           ones too, run with the knobs of t/knobs.sh and each test's own
           `# env:`, as t/run.sh runs them
  unit     the runtime's own test of the matcher's limit, in the copy

A record of step 19, and not part of make test: each breakage is a piece
of the text as it was then, and one that no longer matches stops the
run."""
import subprocess, glob, sys, os, shutil, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, 't')
import checks

RE_C = 'runtime/regex.c'
RE_TS = 'compiler/src/regex.ts'
GEN = 'compiler/src/codegen.ts'
CHECK = 'compiler/src/checker.ts'
PARSE = 'compiler/src/parser.ts'
LEX = 'compiler/src/lexer.ts'
SHAPES = 'compiler/src/shapes.ts'
C_FILES = (RE_C,)
MUTATIONS = [
 # ---- the compiler of a pattern
 ("a lazy star is greedy", RE_TS, "                code[top + 1] = n.lazy ? out : top + 3;", "                code[top + 1] = top + 3;"),
 ("a lazy count is greedy", RE_TS, "                code[s + 1] = n.lazy ? out : s + 3;", "                code[s + 1] = s + 3;"),
 ("alternatives are tried from the last", RE_TS, "            n.alts.forEach((a, k) => {", "            [...n.alts].reverse().forEach((a, k) => {"),
 ("the least count is one short", RE_TS, "            for (let k = 0; k < n.min; k++) gen(n.body);", "            for (let k = 0; k < n.min - 1; k++) gen(n.body);"),
 ("the most count is one short", RE_TS, "            for (let k = n.min; k < n.max; k++) {", "            for (let k = n.min; k < n.max - 1; k++) {"),
 ("/i is lost on a character", RE_TS, "            if (icase && ((n.c >= 0x41", "            if (false && ((n.c >= 0x41"),
 ("/i is lost on a class", RE_TS, "        if (icase) {\n            for (const [lo, hi] of [...ranges]) {", "        if (false) {\n            for (const [lo, hi] of [...ranges]) {"),
 ("/m is lost on ^", RE_TS, "n.a === '^' ? (multi ? OP.MBOL : OP.BOL)", "n.a === '^' ? OP.BOL"),
 ("/m is lost on $", RE_TS, "n.a === '$' ? (multi ? OP.MEOL : OP.EOL)", "n.a === '$' ? OP.EOL"),
 ("/s is lost", RE_TS, "emit(single ? OP.ANYNL : OP.ANY)", "emit(OP.ANY)"),
 ("\\Z is \\z", RE_TS, "n.a === 'Z' ? OP.EOL", "n.a === 'Z' ? OP.EOS"),
 ("\\A is ^ under /m", RE_TS, "n.a === 'A' ? OP.BOL", "n.a === 'A' ? (multi ? OP.MBOL : OP.BOL)"),
 ("\\B is \\b", RE_TS, ": n.a === 'b' ? OP.WORDB : OP.NWORDB;", ": OP.WORDB;"),
 ("a group saves its start in the next one's place", RE_TS, "            if (n.n > 0) emit(OP.SAVE, 2 * n.n);", "            if (n.n > 0) emit(OP.SAVE, 2 * n.n + 2);"),
 ("a class's ^ is lost", RE_TS, "            let flags = n.neg ? NEGATED : 0;", "            let flags = 0;"),
 ("a range's last character is out", RE_TS, "                ranges.push([lo as number, hi as number]);", "                ranges.push([lo as number, (hi as number) - 1]);"),
 ("/x keeps the blanks", RE_TS, "        if (!extended) return;", "        return;"),
 ("/x keeps comments", RE_TS, "            else if (peek() === 0x23) {", "            else if (false) {"),
 ("a backreference inside its group is taken", RE_TS, "                if (!closed.has(n)) refuse(", "                if (n > groups) refuse("),
 ("a quantifier on what can be empty is taken", RE_TS, "        if (nullable(atom)) refuse(", "        if (false) refuse("),
 ("a capture inside a repeat is taken", RE_TS, "        if (hasGroup(atom) && !(atom.k === 'group'", "        if (false && !(atom.k === 'group'"),
 ("a $ in the middle is taken", RE_TS, "            if (next >= 0 && next !== 0x29 && next !== 0x7C && !(", "            if (false && !("),
 ("{n}? is taken", RE_TS, "            if (min === max) refuse(", "            if (false) refuse("),
 ("\\n is a carriage return", RE_TS, "{ n: 10, t: 9,", "{ n: 13, t: 9,"),
 ("\\x{...} is decimal", RE_TS, "                const v = parseInt(String.fromCodePoint(...cs.slice(from, i)), 16);\n                i += 1;\n                return checkChar(v, k);\n            }\n            const from", "                const v = parseInt(String.fromCodePoint(...cs.slice(from, i)), 10);\n                i += 1;\n                return checkChar(v, k);\n            }\n            const from"),
 ("a backslash before punctuation is refused", RE_TS, "        if (c >= 0 && c < 0x80 && !isAlnum(c) && c !== 0x0A) { i += 1; return c; }", ""),
 ("a character past ASCII under /i is taken", RE_TS, "Node => {\n        if (icase && c > 0x7F) refuse(", "Node => {\n        if (false) refuse("),
 ("the empty pattern is taken", RE_TS, "    if (end === 0) refuse(", "    if (false) refuse("),
 ("'--' first in a class is taken", RE_TS, "                if (first && cs[i + 1] === 0x2D) refuse(", "                if (false) refuse("),
 ("an unknown flag is taken", RE_TS, "        refuse(`'${f}' after a pattern is no flag", "        if (f === 'q') continue;\n        refuse(`'${f}' after a pattern is no flag"),
 # ---- the lexer and the parser
 ("a slash never begins a pattern", LEX, "        } else if (c === '/' && !afterValue()) {", "        } else if (false) {"),
 ("a pattern ends at an escaped slash", LEX, "                if (src[k] === '\\\\') k += 1;\n                else if (src[k] === '/') { end = k; break; }", "                if (src[k] === '\\\\') k += 0;\n                else if (src[k] === '/') { end = k; break; }"),
 ("m takes any delimiter", LEX, "            if (src[i + 1] !== '/' && BRACKETS[src[i + 1]!] === undefined) {", "            if (false) {"),
 ("$1 is taken for a name", LEX, "            if (isDigit(at()) || at() === '&'", "            if (at() === '&'"),
 ("!~ is =~", PARSE, "{ kind: 'match', subject: left, negate: true, regex, pos: t.pos }", "{ kind: 'match', subject: left, regex, pos: t.pos }"),
 ("! before the left side is taken", PARSE, "        if (first.kind === 'unary' && !first.bracketed && prefixOp(first.op)?.bang) {\n            refuse(`'${first.op}' before the left side", "        if (false) {\n            refuse(`'${first.op}' before the left side"),
 ("an array on the left is taken", PARSE, "        if (many) refuse(", "        if (false) refuse("),
 ("/g with !~ is taken", PARSE, "        if (t.text === '!~' && regex.global) refuse(", "        if (false) refuse("),
 ("a pattern alone is taken for $_", PARSE, "        if (t.kind === 'match') return refuse('a pattern alone", "        if (false) return refuse('a pattern alone"),
 ("/g where one value is wanted is taken", CHECK, "    if (e.kind === 'match' && e.regex.global) refuse(", "    if (false) refuse("),
 ("a match is never list-shaped", SHAPES, "    case 'match': return e.negate !== true && (e.regex.global || e.regex.groups >= 2);", "    case 'match': return false;"),
 ("a match of one group is list-shaped", SHAPES, "(e.regex.global || e.regex.groups >= 2)", "(e.regex.global || e.regex.groups >= 1)"),
 ("a match is one value among a call's arguments", GEN, "        || (e.kind === 'match' && e.negate !== true)\n", ""),
 ("a match is one value where a list is wanted", GEN, "    } else if (e.kind === 'match' && e.negate !== true) {", "    } else if (false) {"),
 ("!~ is =~ in the C", GEN, "${e.negate ? 'rt_match_not' : 'rt_match'}", "rt_match"),
 # ---- the matcher
 ("a character is one byte", RE_C, "            if (pos < len && (c = decode(s + pos, &size)) == (uint32_t)code[pc + 1]) { pos += size; pc += 2; continue; }", "            if (pos < len && (c = decode(s + pos, &size)) == (uint32_t)code[pc + 1]) { pos += 1; pc += 2; continue; }"),
 ("/i folds nothing", RE_C, "                if (c >= 'A' && c <= 'Z') c |= 0x20;\n                if (c == (uint32_t)code[pc + 1])", "                if (c == (uint32_t)code[pc + 1])"),
 (". takes a newline", RE_C, "            if (pos < len && s[pos] != '\\n') {", "            if (pos < len) {"),
 ("^ under /m after the last newline", RE_C, "            if (pos == 0 || (s[pos - 1] == '\\n' && pos < len)) { pc += 1; continue; }", "            if (pos == 0 || s[pos - 1] == '\\n') { pc += 1; continue; }"),
 ("$ is not before a last newline", RE_C, "            if (pos == len || (pos == len - 1 && s[pos] == '\\n')) { pc += 1; continue; }", "            if (pos == len) { pc += 1; continue; }"),
 ("$ under /m is $", RE_C, "            if (pos == len || s[pos] == '\\n') { pc += 1; continue; }", "            if (pos == len || (pos == len - 1 && s[pos] == '\\n')) { pc += 1; continue; }"),
 ("\\b sees no character before", RE_C, "            int left = b >= 0 && re_word((uint32_t)b);", "            int left = 0;"),
 ("an alternative is tried before the first", RE_C, "            re_push(m, code[pc + 2], pos);\n            pc = code[pc + 1];", "            re_push(m, code[pc + 1], pos);\n            pc = code[pc + 2];"),
 ("a capture is not put back", RE_C, "                m->caps[-1 - a] = b;\n", ""),
 ("captures live on from the last start", RE_C, "    for (int32_t k = 0; k < 2 * (m->re->groups + 1); k++) m->caps[k] = -1;\n", "    if (start == 0) for (int32_t k = 0; k < 2 * (m->re->groups + 1); k++) m->caps[k] = -1;\n"),
 ("a backreference to nothing is empty", RE_C, "            if (from < 0 || to < 0) goto fail;\n            int64_t n = to - from;", "            if (from < 0 || to < 0) { pc += 2; continue; }\n            int64_t n = to - from;"),
 ("a backreference under /i folds nothing", RE_C, "                if (code[pc] == RE_BACKREFI) {", "                if (0) {"),
 ("a /g match of no length may come again", RE_C, "            if (pos == notempty && m->caps[0] == pos) goto fail;", "            if (0) goto fail;"),
 ("a /g match goes on one past the last", RE_C, "        from = m.caps[1];", "        from = m.caps[1] + 1;"),
 ("/i past ASCII is taken", RE_C, "    if (re->icase && s->len != s->chars) rt_fault(", "    if (0) rt_fault("),
 ("the limit is one step short", RE_C, "        if (++m->steps > RE_STEPS)", "        if (++m->steps >= RE_STEPS)"),
 ("no limit at all", RE_C, "        if (++m->steps > RE_STEPS)", "        if (0)"),
 ("a match with no group gives what it matched", RE_C, "    if (nfound > 0 && groups == 0 && !re->global) {", "    if (0) {"),
 ("a group that took no part is the empty string", RE_C, "    if (from < 0 || to < 0) return rt_undef();", "    if (from < 0 || to < 0) return rt_string(&STR_FALSE);"),
 ("a capture counts bytes for characters", RE_C, "    for (int64_t k = from; k < to; k++) chars += !continues(subject->bytes[k]);", "    chars = (uint64_t)(to - from);"),
 ("\\w is \\d", RE_C, "    if (!in && (flags & 4)) in = re_word(c);", "    if (!in && (flags & 4)) in = re_in(RE_TABLE(RE_D), c);"),
 ("\\S is \\s", RE_C, "    if (!in && (flags & 64)) in = !re_in(RE_TABLE(RE_S), c);", "    if (!in && (flags & 64)) in = re_in(RE_TABLE(RE_S), c);"),
 ("a class's ^ is lost in the matcher", RE_C, "    return (flags & 1) ? !in : in;", "    return in;"),
 ("a table's range loses its last character", RE_C, "        else if (c > t[2 * mid + 1]) lo = mid + 1;", "        else if (c >= t[2 * mid + 1]) lo = mid + 1;"),
 ("no match is tried at the end", RE_C, "    for (int64_t at = from; at <= m->len;) {", "    for (int64_t at = from; at < m->len;) {"),
 ("a start may be in the middle of a character", RE_C, "        decode(m->s + at, &size);\n        at += size;", "        decode(m->s + at, &size);\n        at += 1;"),
 # ---- the independent review's rules (D239; T560 to T570), each put out
 ("review: ** after a pattern is taken", PARSE, "        if (peek().kind === 'op' && peek().text === '**') {", "        if (false) {"),
 ("review: a !~ match on the left is taken", PARSE, "        if (left.kind === 'match' && left.negate && !left.bracketed) {", "        if (false) {"),
 ("review: a bracketed !~ match on the left is refused", PARSE, "        if (left.kind === 'match' && left.negate && !left.bracketed) {", "        if (left.kind === 'match' && left.negate) {"),
 ("review: one hex digit is taken", RE_TS, "            if (i === from + 1) refuse('\\\\x and one hex digit", "            if (false) refuse('\\\\x and one hex digit"),
 ("review: $# under /x is an anchor and a comment", RE_TS, "!(extended && isBlankX(next))) refuse(", "!(extended && (isBlankX(next) || next === 0x23))) refuse("),
 ("review: a leading zero in a count is taken", RE_TS, "        if (/^0\\d/.test(a) || /^0\\d/.test(b)) refuse(", "        if (false) refuse("),
 ("review: a leading zero in the first count is taken", RE_TS, "        if (/^0\\d/.test(a) || /^0\\d/.test(b)) refuse(", "        if (a !== b && /^0\\d/.test(b)) refuse("),
 ("review: a leading zero in the second count is taken", RE_TS, "        if (/^0\\d/.test(a) || /^0\\d/.test(b)) refuse(", "        if (/^0\\d/.test(a)) refuse("),
 ("review: a delimiter twice in a class is taken", RE_TS, "            if (twice !== undefined) refuse(", "            if (false) refuse("),
 ("review: an escaped delimiter does not count", RE_TS, "raw.includes(d) && raw.split(d).length + escaped.split(d).length > 3", "raw.split(d).length > 2"),
 ("review: a delimiter and letters in a class are taken", RE_TS, "            if (one !== null && /[A-Za-z]{3}/.test(raw)) refuse(", "            if (false) refuse("),
 ("review: a delimiter and two letters are refused", RE_TS, "            if (one !== null && /[A-Za-z]{3}/.test(raw)) refuse(", "            if (one !== null && /[A-Za-z]{2}/.test(raw)) refuse("),
 ("review: a class of nothing by \\S and \\D is taken", RE_TS, " || (has('S') && (has('D') || has('W'))) || (has('D') && has('w'))) {", " || (has('D') && has('w'))) {"),
 ("review: a class of nothing by \\D and \\w is taken", RE_TS, " || (has('S') && (has('D') || has('W'))) || (has('D') && has('w'))) {", " || (has('S') && (has('D') || has('W')))) {"),
 ("review: a class of nothing by \\d and \\D is taken", RE_TS, " || (has('d') && has('D')) || ", " || "),
 ("review: a class of nothing by its ranges is taken", RE_TS, "            if (covers(0, 0x10FFFF) || ", "            if ("),
 ("review: a class of nothing by \\S and the blanks is taken", RE_TS, "(has('S') && BLANKS.every(([lo, hi]) => covers(lo, hi))) || ", ""),
 ("review: any negated class with \\S is refused", RE_TS, "(has('S') && BLANKS.every(([lo, hi]) => covers(lo, hi))) || ", "has('S') || "),
 ("review: \\N{U+} before a blank in a class is taken", RE_TS, "                if (extended && e === 0x4E && (isBlankX(peek()) || peek() === 0x23)) {", "                if (false) {"),
 ("review: \\N{U+} in a class under /x is refused", RE_TS, "                if (extended && e === 0x4E && (isBlankX(peek()) || peek() === 0x23)) {", "                if (extended && e === 0x4E) {"),
 ("review: a lazy quantifier and a wide character are taken", RE_TS, "    if (lazyAt !== undefined && wide) refuse(", "    if (false) refuse("),
 ("review: a wide character in a class is not seen", RE_TS, "        if (ranges.some(([, hi]) => hi > 0xFF)) wide = true;\n", ""),
 ("review: a wide character alone is not seen", RE_TS, "        if (c > 0xFF) wide = true;\n", ""),
 ("review: a character at U+00FF is wide", RE_TS, "        if (c > 0xFF) wide = true;\n", "        if (c >= 0xFF) wide = true;\n"),
 ("review: a count in a repeated group is taken", RE_TS, "        if (min >= 2 && countsAString(atom)) {", "        if (false) {"),
 ("review: a count in a group repeated twice is taken", RE_TS, "        if (min >= 2 && countsAString(atom)) {", "        if (min >= 3 && countsAString(atom)) {"),
 ("review: a count in a group repeated once or more is refused", RE_TS, "        if (min >= 2 && countsAString(atom)) {", "        if (min >= 1 && countsAString(atom)) {"),
 ("review: a class of one character is no string", RE_TS, "        case 'class': return !n.neg && n.escapes.length === 0 && n.ranges.length > 0 && n.ranges.every(([lo, hi]) => lo === hi && lo === n.ranges[0]![0]);", "        case 'class': return false;"),
 ("review: any class is one string", RE_TS, "        case 'class': return !n.neg && n.escapes.length === 0 && n.ranges.length > 0 && n.ranges.every(([lo, hi]) => lo === hi && lo === n.ranges[0]![0]);", "        case 'class': return true;"),
 ("review: a group is no string", RE_TS, "        case 'group': return oneString(n.body);", "        case 'group': return false;"),
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
for src in sorted(glob.glob('t/5[1-6][0-9][0-9]-*.pl')):
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
    """How many of the runtime's own tests of the matcher fail, in the copy."""
    r = subprocess.run(['node', '--test', '--test-name-pattern', 'matcher', f'{tree}/runtime/tests/rt.test.ts'], capture_output=True, text=True)
    return len(re.findall(r'^not ok', r.stdout, re.M)) if r.returncode else 0

def copy():
    shutil.rmtree('build/mut/tree', ignore_errors=True)
    for part in ('bin', 'compiler/src', 'runtime'):
        shutil.copytree(part, 'build/mut/tree/' + part)

def runtime():
    """The copy's runtime, compiled; whether it compiled."""
    return subprocess.run(['cc', '-O1', '-c', '-Ibuild/mut/tree/runtime', '-o', 'build/mut/rt.o', 'build/mut/tree/runtime/rt.c'], capture_output=True).returncode == 0

os.makedirs('build/mut', exist_ok=True)
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
    if path in C_FILES:
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
