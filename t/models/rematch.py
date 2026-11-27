#!/usr/bin/env python3
"""t/5100 to t/5103: pattern matching (step 19; D225 to D237). Named
rematch.py, not re.py, so that no model beside it imports it for
Python's own `re`.

A matcher of its own, by the definition and nothing of the compiler's or
the runtime's: a pattern is read into a tree, and the tree is matched by
continuations, each alternative tried in perl's order (the leftmost
start; an alternative before the next; a greedy count the most first, a
lazy one the fewest), a group's capture set as the match passes its end
and undone as the match backtracks past it. The definition it follows:

  .            any character but a newline; under /s any
  \\d \\w \\s      perl's classes: here over a small alphabet whose
               characters are written down (DIGIT, WORD, SPACE below);
               \\D \\W \\S the rest
  ^ $          the start; the end, or before a newline that ends the
               string. Under /m after any newline but the last one's
               end, and before any newline
  \\A \\z \\Z     the start, the end, $ without /m
  \\b \\B        between a word character and something else, or not
  \\1 to \\9     what that group captured, which must have been set
  /i           ASCII letters either case (no character past ASCII is
               in a subject under /i: D230)
  /g           where a list is wanted: from the start, each match the
               next, a match of no length not again where the last one
               ended if it was of no length too (T544)

Where one value is wanted a match is `1` or the empty string; where a
list is, the captures (undef for a group that took no part), `(1)` with
no group, `()` with no match (D235). perl is the second derivation
(t/checks.py oracle).

5100 is matches where one value is wanted, `=~` and `!~`; 5101 captures
where a list is wanted; 5102 /g; 5103 the flags i, m, s and x.

Every command that writes a file, one a line (t/checks.py runs them all):

    python3 t/models/rematch.py --program 5100 > t/5100-re-tests.pl
    python3 t/models/rematch.py 5100 > t/5100-re-tests.expected
    python3 t/models/rematch.py --program 5101 > t/5101-re-captures.pl
    python3 t/models/rematch.py 5101 > t/5101-re-captures.expected
    python3 t/models/rematch.py --program 5102 > t/5102-re-global.pl
    python3 t/models/rematch.py 5102 > t/5102-re-global.expected
    python3 t/models/rematch.py --program 5103 > t/5103-re-flags.pl
    python3 t/models/rematch.py 5103 > t/5103-re-flags.expected
"""

import random

import sys

sys.setrecursionlimit(20000)

# The alphabet, and which of perl's classes each character is in: the
# Arabic-Indic three is a digit and a word character to perl (T67), the
# no-break space a blank (T545).
ALPHA = 'aabBc 1_-\né٣ '
ASCII = 'aabBcC 1_-\n'
DIGIT = set('1٣')
WORD = set('abcABC1_é٣')
SPACE = set(' \n ')
CLASS = {'d': DIGIT, 'w': WORD, 's': SPACE}

# ---- the tree, read from the pattern the generator wrote

def parse(p):
    i = [0]
    groups = [0]

    def peek():
        return p[i[0]] if i[0] < len(p) else ''

    def take():
        c = p[i[0]]
        i[0] += 1
        return c

    def escape():
        c = take()
        if c in 'dwsDWS':
            return ('class', False, [], [c])
        if c in 'bBAzZ':
            return ('assert', c)
        if c.isdigit():
            return ('backref', int(c))
        if c == 'n':
            return ('char', '\n')
        if c == 'x':
            assert take() == '{'
            h = ''
            while peek() != '}':
                h += take()
            take()
            return ('char', chr(int(h, 16)))
        return ('char', c)

    def klass():
        neg = peek() == '^'
        if neg:
            take()
        ranges, escapes = [], []
        while peek() != ']':
            if peek() == '\\':
                take()
                e = escape()
                if e[0] == 'class':
                    escapes += e[3]
                    continue
                lo = e[1]
            else:
                lo = take()
            if peek() == '-' and p[i[0] + 1] != ']':
                take()
                hi = take()
                if hi == '\\':
                    hi = escape()[1]
                ranges.append((lo, hi))
            else:
                ranges.append((lo, lo))
        take()
        return ('class', neg, ranges, escapes)

    def atom():
        c = take()
        if c == '(':
            if p.startswith('?:', i[0]):
                i[0] += 2
                n = 0
            else:
                groups[0] += 1
                n = groups[0]
            body = alt()
            assert take() == ')'
            return ('group', n, body)
        if c == '.':
            return ('any',)
        if c == '[':
            return klass()
        if c in '^$':
            return ('assert', c)
        if c == '\\':
            return escape()
        return ('char', c)

    def quant(a):
        c = peek()
        if c in ('*', '+', '?'):
            take()
            lo, hi = {'*': (0, None), '+': (1, None), '?': (0, 1)}[c]
        elif c == '{':
            take()
            s = ''
            while peek() != '}':
                s += take()
            take()
            if ',' in s:
                a1, b1 = s.split(',')
                lo, hi = int(a1), (int(b1) if b1 else None)
            else:
                lo = hi = int(s)
        else:
            return a
        lazy = peek() == '?'
        if lazy:
            take()
        return ('rep', a, lo, hi, lazy)

    def seq():
        items = []
        while peek() not in ('', '|', ')'):
            items.append(quant(atom()))
        return ('seq', items)

    def alt():
        alts = [seq()]
        while peek() == '|':
            take()
            alts.append(seq())
        return ('alt', alts)

    tree = alt()
    assert i[0] == len(p), p
    return tree, groups[0]


# ---- the matcher

def matcher(tree, flags, s):
    icase, multi, single = 'i' in flags, 'm' in flags, 's' in flags
    fold = (lambda c: c.lower() if c.isascii() else c) if icase else (lambda c: c)
    word = lambda k: 0 <= k < len(s) and s[k] in WORD

    def inclass(node, c):
        _, neg, ranges, escapes = node
        cc = [c, c.swapcase()] if icase and c.isascii() else [c]
        found = any(lo <= x <= hi for x in cc for lo, hi in ranges)
        for e in escapes:
            members = CLASS[e.lower()]
            found = found or ((c in members) if e.islower() else (c not in members))
        return found != neg

    def m(node, k, caps, cont):
        kind = node[0]
        if kind == 'char':
            return k < len(s) and fold(s[k]) == fold(node[1]) and cont(k + 1, caps)
        if kind == 'any':
            return k < len(s) and (single or s[k] != '\n') and cont(k + 1, caps)
        if kind == 'class':
            return k < len(s) and inclass(node, s[k]) and cont(k + 1, caps)
        if kind == 'assert':
            a = node[1]
            ok = {
                '^': k == 0 or (multi and s[k - 1] == '\n' and k < len(s)),
                'A': k == 0,
                '$': k == len(s) or (multi and s[k] == '\n') or (k == len(s) - 1 and s[k] == '\n'),
                'Z': k == len(s) or (k == len(s) - 1 and s[k] == '\n'),
                'z': k == len(s),
                'b': word(k - 1) != word(k),
                'B': word(k - 1) == word(k),
            }[a]
            return ok and cont(k, caps)
        if kind == 'backref':
            got = caps.get(node[1])
            if got is None:
                return False
            t = s[got[0]:got[1]]
            if fold(s[k:k + len(t)]) != fold(t) or len(s) - k < len(t):
                return False
            return cont(k + len(t), caps)
        if kind == 'group':
            n = node[1]
            if n == 0:
                return m(node[2], k, caps, cont)
            return m(node[2], k, caps, lambda e, c2: cont(e, {**c2, n: (k, e)}))
        if kind == 'seq':
            def go(j, k1, c1):
                if j == len(node[1]):
                    return cont(k1, c1)
                return m(node[1][j], k1, c1, lambda e, c2: go(j + 1, e, c2))
            return go(0, k, caps)
        if kind == 'alt':
            return any(m(a, k, caps, cont) for a in node[1])
        if kind == 'rep':
            _, body, lo, hi, lazy = node

            def rep(count, k1, c1):
                more = lambda: (hi is None or count < hi) and m(body, k1, c1, lambda e, c2: rep(count + 1, e, c2))
                stop = lambda: count >= lo and cont(k1, c1)
                if count < lo:
                    return more()
                return (stop() or more()) if lazy else (more() or stop())
            return rep(0, k, caps)
        raise ValueError(kind)

    def search(start, notempty):
        for k in range(start, len(s) + 1):
            found = []

            def done(e, caps, k=k):
                if e == notempty and k == e:
                    return False
                found.append((k, e, caps))
                return True
            if m(tree, k, {}, done):
                return found[0]
        return None
    return search


def match_list(pattern, flags, glob, s):
    tree, groups = parse(pattern)
    search = matcher(tree, flags, s)
    out, start, notempty = [], 0, -1
    while True:
        got = search(start, notempty)
        if got is None:
            break
        k, e, caps = got
        if groups == 0:
            out.append(s[k:e] if glob else 1)
        else:
            out += [s[caps[n][0]:caps[n][1]] if n in caps else None for n in range(1, groups + 1)]
        if not glob:
            break
        start, notempty = e, (e if k == e else -1)
    return out


def matches(pattern, flags, s):
    tree, _ = parse(pattern)
    return matcher(tree, flags, s)(0, -1) is not None


# ---- the programs: patterns the language takes, by construction (no
# capture inside a repeat, no quantifier on what can be empty, a
# backreference to a group closed before it, a $ last)

def gen_pattern(r, depth=2, ascii_only=False):
    groups = [0]
    closed = []

    def literal():
        pool = 'abcB 1_-' if ascii_only else 'abcB 1_-é'
        c = r.choice(pool)
        return {'é': '\\x{e9}', ' ': ' ', '-': '\\-'}.get(c, c)

    def atom(in_rep, need_solid):
        k = r.random()
        if k < 0.35:
            return literal(), True
        if k < 0.42:
            return '.', True
        if k < 0.55:
            neg = '^' if r.random() < 0.3 else ''
            items = ''.join(r.choice(['a', 'b', 'a-c', '\\d', '\\w', '\\s', ' ', '_', '1'] + ([] if ascii_only else ['\\x{e9}'])) for _ in range(r.randint(1, 3)))
            return f'[{neg}{items}]', True
        if k < 0.65:
            return r.choice(['\\d', '\\w', '\\s', '\\D', '\\W', '\\S']), True
        if k < 0.72 and not need_solid:
            return r.choice(['^', '\\b', '\\B', '\\A']), False
        if k < 0.76 and closed and not need_solid:
            return f'\\{r.choice(closed)}', False
        if depth > 0 and r.random() < 0.7:
            cap = not in_rep and r.random() < 0.6
            n = 0
            if cap:
                groups[0] += 1
                n = groups[0]
            inner = alt(depth - 1, in_rep, True)
            if n:
                closed.append(n)
            return (f'({inner})' if cap else f'(?:{inner})'), True
        return literal(), True

    def piece(d, in_rep):
        a, solid = atom(in_rep, False)
        if solid and r.random() < 0.4:
            q = r.choice(['*', '+', '?', '{2}', '{1,2}', '{0,2}', '{2,}'])
            if q != '{2}' and r.random() < 0.3:
                q += '?'
            # A group with a capturing group in it, repeated, is refused
            # (D231); one whose body could be empty is too, which `solid`
            # rules out.
            inner = a[3:] if a.startswith('(?:') else a[1:] if a.startswith('(') else ''
            if any(inner[k] == '(' and not inner.startswith('?:', k + 1) for k in range(len(inner))):
                return a
            return a + q
        return a

    def alt(d, in_rep, solid):
        n = 1 if r.random() < 0.75 else 2
        alts = []
        for _ in range(n):
            ps = [piece(d, in_rep) for _ in range(r.randint(1, 3))]
            # Each alternative has a character in it, so that a group
            # holding it can be repeated.
            if solid:
                ps.append(literal())
            alts.append(''.join(ps))
        return '|'.join(alts)

    depth_ = depth
    body = alt(depth_, False, False)
    if r.random() < 0.15:
        body += '$'
    return body


def lit(s):
    out = ''
    for ch in s:
        out += {'\n': '\\n', '"': '\\"', '\\': '\\\\', '$': '\\$', '@': '\\@', 'é': '\\x{e9}', '٣': '\\x{663}', ' ': '\\x{a0}'}.get(ch, ch)
    return '"' + out + '"'


def show(v):
    return 'u' if v is None else str(v)


def build(test):
    r = random.Random(test)
    lines, out = [], []
    n = 0
    while n < 220:
        flags = ''
        if test == 5103:
            flags = ''.join(f for f in 'imsx' if r.random() < 0.5)
        ascii_only = 'i' in flags
        pattern = gen_pattern(r, ascii_only=ascii_only)
        src = pattern.replace(' ', '\\ ') if 'x' in flags else pattern
        if 'x' in flags:
            src = ' ' + src.replace('|', ' | ') + ' '
        pool = ASCII if ascii_only else ALPHA
        s = ''.join(r.choice(pool) for _ in range(r.randint(0, 7)))
        if test in (5100, 5103) and r.random() < 0.5 or test == 5100:
            yes = matches(pattern, flags, s)
            op = r.choice(['=~', '!~'])
            lines.append(f'say {lit(s)} {op} /{src}/{flags} ? "y" : "n";')
            out.append('y' if yes == (op == '=~') else 'n')
            # And as a value: a boolean, 1 or the empty string.
            lines.append(f'say "[", ({lit(s)} =~ /{src}/{flags}) . "", "]";')
            out.append('[' + ('1' if yes else '') + ']')
        else:
            glob = test == 5102
            got = match_list(pattern, flags, glob, s)
            lines.append(f'say join("|", map {{ $_ // "u" }} ({lit(s)} =~ /{src}/{flags}{"g" if glob else ""})), ".";')
            out.append('|'.join(show(v) for v in got) + '.')
        n += 1
    return lines, out


HEAD = {
    5100: 'matches where one value is wanted, =~ and !~',
    5101: 'captures where a list is wanted',
    5102: '/g where a list is wanted',
    5103: 'the flags i, m, s and x',
}


def main(argv):
    program = argv[0] == '--program'
    test = int(argv[-1])
    lines, out = build(test)
    if program:
        print(f'# t/models/rematch.py {test}: {HEAD[test]} (step 19)')
        print('use v5.42;')
        print('use utf8;')
        print('use open ":std", ":encoding(UTF-8)";')
        print('\n'.join(lines))
    else:
        print('\n'.join(out))


if __name__ == '__main__':
    main(sys.argv[1:])
