#!/usr/bin/env python3
"""A seeded generator of whole programs in the language, across its
features, for the differential fuzzer (run.py; README.md here).

    python3 docs/briefs/fuzz/gen.py SEED      # one program on stdout

A program is a tree, so that run.py can take out the statement a refusal
or a fault names and ask again (`render`, `delete_at`): a block is
{'stmts': [...], 'need': bool}, a statement is a list of parts, each a
string (its text, lines and all) or a block. The generator knows the
language roughly, not exactly: it keeps the programs that compile at a
useful rate, and leaves the rest to the compiler, whose refusals are
counted and repaired, never trusted to be right.

What it leans on, each a place a WRONG was found or feared before:
a variable read and changed in one statement (D14, D57, D69, D76, D80,
T230), elements and chains through references (D109), loops whose
lists name what their blocks change (D17, D77), closures over loop
variables (D162), what a call gives in each context (D18, D71), numbers
at 2^53 and 2^63 and the soft strings (D35, D40, D45), and every
operator on every kind of value. A program never builds what is large
(T351, D46), every loop is counted by a variable nothing else touches
(T131), and a hash's order is never printed (D27).
"""
import random
import re
import sys

INTS = ['0', '1', '2', '3', '7', '10', '-1', '-3', '255', '1_000',
        '9007199254740992', '9007199254740993', '9007199254740991',
        '9223372036854775807', '4611686018427387904', '0x7F', '0b101', '0o17',
        '1000000000000000', '999999999999999', '4294967296', '65536']
NUMS = ['1.5', '0.1', '2.5', '1e3', '.5', '3.0', '1e15', '1e16', '2.5e-3',
        '0.30000000000000004', '9007199254740992.0', '1e300', '-0.0', '0.0',
        '123.456', '1e-5', '4.5']
NSTRS = ['"3.0"', '"12"', '"1e3"', '"0.5"', '"-7"', '"0"', '"0.0"', '"10"',
         '"9007199254740993"', '"9007199254740992"', '"1.5e1"', '" 4"', '"4 "',
         '"+5"', '"-0"', '"007"', '"2.50"', '"1e20"', '"1_000"', '"0x10"', '"abc"',
         '"12abc"', '""', '"inf"', '"nan"', '".5"', '"5."']
STRS = ['"abc"', '"a"', '""', '"0"', "'x y'", '"Hello"', '"b\\n"', '"tab\\there"',
        "'q'", '"zz"', '"A"', '"a\\tb"', '"\\x41"', '"\\x{263A}"', '"\\0"', '"ab\\n\\n"',
        '"\\N{U+E9}"', '"-"', '"10"', '"x"']
WORDS = ['k', 'a', 'b', 'key', 'x1', 'zz', 'n']
LETTERS = 'abcdefghijklmnopqrstuvw'


def blk(stmts=None, need=False):
    return {'stmts': stmts if stmts is not None else [], 'need': need}


class Scope:
    def __init__(self, parent=None, kind='block'):
        self.parent = parent
        self.vars = {}          # name with sigil -> info dict
        self.kind = kind

    def all(self):
        s, out = self, {}
        while s:
            for k, v in s.vars.items():
                out.setdefault(k, v)
            s = s.parent
        return out


class Gen:
    def __init__(self, seed):
        self.r = random.Random(seed)
        self.seed = seed
        self.n = 0
        self.scope = Scope(kind='file')
        self.subs = {}            # name -> info
        self.loop_labels = []     # labels of loops we are in (None for unlabelled)
        self.in_sub = None        # info of the sub we are in
        self.in_anon = 0
        self.in_block_expr = 0    # inside a map/grep/sort block: $_ $a $b
        self.topics = []          # what $_ is in the innermost binders
        self.sortvars = False
        self.needs_utf8 = False
        self.depth_loops = 0
        self.frozen = set()
        self.recent = []
        # a dense program: no loops or subs, statement after statement of
        # values read and changed in one go
        self.dense = self.r.random() < 0.3

    # ---- helpers
    def p(self, x):
        return self.r.random() < x

    def ch(self, xs):
        return self.r.choice(xs)

    def fresh(self, base):
        self.n += 1
        return f'{base}{self.n}'

    def vars(self, sigil, kinds=None, writable=False):
        out = []
        for name, info in self.scope.all().items():
            if name[0] != sigil:
                continue
            if writable and info.get('ro'):
                continue
            if kinds and info.get('kind') not in kinds:
                continue
            out.append(name)
        return sorted(out)

    def declare(self, name, **info):
        self.scope.vars[name] = info

    def push(self, kind='block'):
        self.scope = Scope(self.scope, kind)

    def pop(self):
        self.scope = self.scope.parent

    def pick(self, xs):
        """A name, by preference one this statement has named already: a
        variable read and changed in one statement is what the walks of
        order (D14, D57, D76, D80) are about."""
        again = [x for x in xs if x in self.recent]
        x = self.ch(again) if again and self.p(0.75 if self.dense else 0.55) else self.ch(xs)
        self.recent.append(x)
        return x

    # ---- leaves
    def int_lit(self):
        if self.p(0.6):
            return str(self.r.randint(0, 12))
        return self.ch(INTS)

    def num_lit(self):
        return self.ch(NUMS)

    def str_lit(self):
        if self.p(0.3):
            return self.ch(NSTRS)
        if self.p(0.15):
            return self.interp()
        s = self.ch(STRS)
        if '\\x{263A}' in s or '\\N{U+E9}' in s:
            self.needs_utf8 = True
        return s

    def interp(self):
        """A double-quoted string with variables in it, of the shapes
        D91, D92, D99 and 13d take."""
        pieces = []
        for _ in range(self.r.randint(1, 3)):
            pieces.append(self.ch(['<', ' x', ' ', '|', '-', ':', '=']))
            v = self.interp_piece()
            if v:
                pieces.append(v)
        pieces.append(self.ch(['>', '.', '!', ' ', '|']))
        return '"' + ''.join(pieces) + '"'

    def interp_piece(self):
        opts = []
        sc = self.vars('$', {'int', 'num', 'str', 'nstr', 'bool'})
        arr = self.vars('@')
        hs = self.vars('%')
        if sc:
            opts += ['s'] * 4
        if arr:
            opts += ['a'] * 3
        if hs:
            opts += ['h'] * 2
        refs = self.vars('$', {'aref', 'href', 'sref'})
        if refs:
            opts += ['r'] * 3
        if self.topics:
            opts += ['t']
        if not opts:
            return None
        k = self.ch(opts)
        idx = lambda: self.ch(['0', '1', '-1', '2'] + [v for v in sc if self.scope.all()[v].get('kind') == 'int'][:2])
        if k == 's':
            v = self.ch(sc)
            return self.ch([v, '${' + v[1:] + '}'])
        if k == 't':
            return '$_'
        if k == 'a':
            a = self.ch(arr)
            return self.ch([a, f'${a[1:]}[{idx()}]', f'@{{{a[1:]}}}', f'$#{a[1:]}', f'{a}[0, 1]', f'{a}[0 .. 1]'])
        if k == 'h':
            h = self.ch(hs)
            key = self.ch(WORDS + [v for v in sc if self.scope.all()[v].get('kind') == 'str'][:2])
            return f'${h[1:]}{{{key}}}'
        r = self.ch(refs)
        kind = self.scope.all()[r]['kind']
        if kind == 'aref':
            return self.ch([f'{r}->[{idx()}]', f'{r}->@*', f'@{{{r}}}', f'$#{{{r}}}', f'{r}->$#*', f'{r}->@[0, 1]'])
        if kind == 'href':
            return self.ch([f'{r}->{{{self.ch(WORDS)}}}'])
        return self.ch([f'{r}->$*', f'${{{r}}}'])

    # ---- expressions
    def expr(self, d, want=None):
        """A value: want is 'num', 'str', 'bool', 'ref' or None for any."""
        if want is None:
            want = self.ch(['num', 'num', 'str', 'str', 'bool', 'ref', 'any'])
        if want == 'any':
            want = self.ch(['num', 'str', 'bool'])
        if self.dense and d > 0 and want in ('num', 'str') and self.p(0.2):
            return self.side(d - 1, want)
        if d <= 0 or self.p(0.25):
            return self.leaf(want)
        f = getattr(self, 'e_' + want)
        return f(d - 1)

    def br(self, s):
        return f'({s})'

    def leaf(self, want):
        cands = []
        if want == 'num':
            cands = self.vars('$', {'int', 'num', 'nstr', 'bool'})
            if self.p(0.1):
                return self.ch(NSTRS[:12])
            if self.p(0.5) or not cands:
                return self.ch([self.int_lit, self.int_lit, self.num_lit])()
        elif want == 'str':
            cands = self.vars('$', {'str', 'nstr', 'int'})
            if self.p(0.5) or not cands:
                return self.str_lit()
        elif want == 'bool':
            if self.p(0.4):
                return self.ch(['true', 'false', '!!1', '(1 == 1)', '(0 > 1)', '!1', '!0'])
            cands = self.vars('$', {'bool', 'int', 'str'})
            if not cands:
                return 'true'
        elif want == 'ref':
            cands = self.vars('$', {'aref', 'href', 'sref', 'code'})
            if not cands or self.p(0.3):
                return self.anon(1)
        if self.topics and self.p(0.3) and want in ('num', 'str'):
            return '$_'
        if self.sortvars and self.p(0.3):
            return self.ch(['$a', '$b'])
        return self.pick(cands)

    def anon(self, d):
        k = self.ch(['a', 'a', 'h', 's'])
        if k == 'a':
            return '[' + ', '.join(self.expr(d - 1, self.ch(['num', 'str'])) for _ in range(self.r.randint(0, 3))) + ']'
        if k == 'h':
            return '{' + ', '.join(f'{self.ch(WORDS)} => {self.expr(d - 1, self.ch(["num", "str"]))}' for _ in range(self.r.randint(0, 3))) + '}'
        sc = self.vars('$', writable=True)
        sc = [v for v in sc if not self.scope.all()[v].get('loopvar')]
        if sc:
            return '\\' + self.ch(sc)
        return '[]'

    def place(self, d, kinds=None):
        """Something assignable: a scalar, an element, a chain, or through
        a scalar reference."""
        opts = []
        sc = [v for v in self.vars('$', writable=True) if not self.scope.all()[v].get('const')]
        if kinds:
            sck = [v for v in sc if self.scope.all()[v].get('kind') in kinds]
        else:
            sck = sc
        if sck:
            opts += ['s'] * 6
        if self.vars('@'):
            opts += ['ae'] * 2
        if self.vars('%'):
            opts += ['he'] * 2
        if self.vars('$', {'aref'}):
            opts += ['ra']
        if self.vars('$', {'href'}):
            opts += ['rh']
        if self.vars('$', {'sref'}):
            opts += ['rs']
        if not opts:
            return None
        k = self.ch(opts)
        if k == 's':
            return self.pick(sck)
        return self.elem(d, k)

    def index(self, d):
        if d > 0 and self.p(0.08):
            # an index that does something: a step, an assignment, a call
            return self.ch([lambda: self.side(0, 'num'), lambda: self.call(0, 'num')])()
        if self.p(0.6):
            return self.ch(['0', '1', '2', '-1', '3'])
        sc = self.vars('$', {'int'})
        if sc and self.p(0.6):
            return self.ch(sc)
        return self.ch(['$#', '1 + ', '-']) [0:0] + self.ch(['(1 + 1)', '(3 - 4)', '(2 * 1)', f'(0 + {self.ch(sc) if sc else "1"})'])

    def key(self, d):
        if self.p(0.6):
            return self.ch(WORDS)
        sc = self.vars('$', {'str', 'int'})
        if sc and self.p(0.5):
            return self.ch(sc)
        return self.expr(min(d, 1), 'str')

    def elem(self, d, k=None):
        if k is None:
            opts = []
            if self.vars('@'):
                opts.append('ae')
            if self.vars('%'):
                opts.append('he')
            if self.vars('$', {'aref'}):
                opts.append('ra')
            if self.vars('$', {'href'}):
                opts.append('rh')
            if not opts:
                return None
            k = self.ch(opts)
        if k == 'ae':
            a = self.pick(self.vars('@'))
            e = f'${a[1:]}[{self.index(d)}]'
            if self.p(0.15):
                e += self.ch([f'[{self.index(0)}]', f'{{{self.ch(WORDS)}}}'])
            return e
        if k == 'he':
            h = self.pick(self.vars('%'))
            e = f'${h[1:]}{{{self.key(d)}}}'
            if self.p(0.15):
                e += self.ch([f'[{self.index(0)}]', f'{{{self.ch(WORDS)}}}'])
            return e
        if k == 'ra':
            r = self.pick(self.vars('$', {'aref'}))
            e = f'{r}->[{self.index(d)}]'
            if self.p(0.2):
                e += self.ch([f'[{self.index(0)}]', f'{{{self.ch(WORDS)}}}'])
            return e
        if k == 'rh':
            r = self.pick(self.vars('$', {'href'}))
            e = f'{r}->{{{self.key(d)}}}'
            if self.p(0.2):
                e += self.ch([f'[{self.index(0)}]', f'{{{self.ch(WORDS)}}}'])
            return e
        r = self.ch(self.vars('$', {'sref'}))
        return self.ch([f'{r}->$*', f'${{{r}}}'])

    def side(self, d, want):
        """An assignment or a step inside an expression: what the walks
        of order are for."""
        pl = self.place(d, {'int', 'num', 'nstr', 'bool', 'undef'} if want == 'num' else None)
        if pl is None:
            return self.leaf(want)
        k = self.r.random()
        if k < 0.3 and want in ('num', 'bool'):
            return self.ch([f'++{pl}', f'--{pl}', f'{pl}++', f'{pl}--'])
        op = self.ch(['=', '=', '+=', '-=', '*=', '.=', '||=', '//=', '&&=', 'x=', '**=', '%=', '/='])
        rhs = self.expr(d, 'str' if op in ('.=',) else ('num' if op not in ('=', '||=', '//=', '&&=') else want if want != 'bool' else 'num'))
        if op == 'x=':
            rhs = self.ch(['0', '1', '2', '3'])
        if op in ('**=',):
            rhs = self.ch(['2', '3', '0', '0.5'])
        return f'({pl} {op} {rhs})'

    def e_num(self, d):
        k = self.r.random()
        if k < 0.30:
            op = self.ch(['+', '-', '*', '+', '-', '*', '/', '%', '**'])
            a, b = self.expr(d, 'num'), self.expr(d, 'num')
            if op == '**':
                b = self.ch(['2', '3', '0', '-1', '0.5', '10', '53', '62', '63', '64'])
            if op in ('/', '%') and self.p(0.7):
                b = self.ch(['2', '3', '-2', '7', '0.5', '1e3'])
            s = f'{a} {op} {b}'
            return self.br(s) if self.p(0.85) else s
        if k < 0.40:
            return self.side(d, 'num')
        if k < 0.46:
            return self.ch(['-', '+']) + self.br(self.expr(d, 'num'))
        if k < 0.55:
            f = self.ch(['length', 'ord', 'index', 'rindex', 'scalar', 'count', 'lastidx', 'cmp', 'spaceship'])
            if f == 'length':
                return f'length({self.expr(d, "str")})'
            if f == 'ord':
                return f'ord({self.expr(d, "str")})'
            if f in ('index', 'rindex'):
                extra = f', {self.ch(["0", "1", "-1", "2", "10"])}' if self.p(0.4) else ''
                return f'{f}({self.expr(d, "str")}, {self.expr(d, "str")}{extra})'
            if f == 'scalar':
                a = self.vars('@')
                if a:
                    return f'scalar({self.ch(a)})'
                return '0'
            if f == 'count':
                a = self.vars('%')
                if a:
                    return self.ch([f'scalar(%{self.ch(a)[1:]})', f'scalar(keys %{self.ch(a)[1:]})'])
                return '1'
            if f == 'lastidx':
                a = self.vars('@')
                r = self.vars('$', {'aref'})
                if a and (not r or self.p(0.5)):
                    return f'$#{self.ch(a)[1:]}'
                if r:
                    return self.ch([f'$#{{{self.ch(r)}}}', f'{self.ch(r)}->$#*', f'scalar({self.ch(r)}->@*)'])
                return '2'
            if f == 'cmp':
                return self.br(f'{self.expr(d, "str")} cmp {self.expr(d, "str")}')
            return self.br(f'{self.expr(d, "num")} <=> {self.expr(d, "num")}')
        if k < 0.65:
            e = self.elem(d)
            if e:
                return f'({e} // {self.ch(["0", "1", "-1", "2.5"])})' if self.p(0.75) else e
            return self.leaf('num')
        if k < 0.72:
            return self.call(d, 'num')
        if k < 0.78:
            return self.ternary(d, 'num')
        if k < 0.83:
            return self.logic(d, 'num')
        if k < 0.87:
            # a list where one value is wanted: a count
            ch = self.r.random()
            if ch < 0.5:
                return f'(0 + grep {{ {self.blockexpr(d, "bool")} }} {self.listexpr(d)})'
            return f'(0 + map {{ {self.blockexpr(d, "num")} }} {self.listexpr(d)})'
        if k < 0.92:
            return f'({self.listexpr(d)})[{self.index(0)}]'
        return self.leaf('num')

    def e_str(self, d):
        k = self.r.random()
        if k < 0.25:
            a, b = self.expr(d, 'str'), self.expr(d, self.ch(['str', 'num']))
            n = self.r.randint(0, 2)
            s = f'{a} . {b}'
            for _ in range(n):
                s += ' . ' + self.expr(d, self.ch(['str', 'num']))
            return self.br(s) if self.p(0.8) else s
        if k < 0.32:
            return self.br(f'{self.expr(d, "str")} x {self.ch(["0", "1", "2", "3", "-1", "2.5"])}')
        if k < 0.45:
            f = self.ch(['uc', 'lc', 'ucfirst', 'lcfirst', 'substr', 'substr3', 'chr', 'sprintf', 'join', 'ref', 'reverse'])
            if f in ('uc', 'lc', 'ucfirst', 'lcfirst'):
                return f'{f}({self.expr(d, "str")})'
            if f == 'substr':
                return f'substr({self.expr(d, "str")}, {self.ch(["0", "1", "-1", "2", "-2", "5"])})'
            if f == 'substr3':
                return f'substr({self.expr(d, "str")}, {self.ch(["0", "1", "-1", "2"])}, {self.ch(["0", "1", "2", "-1", "10"])})'
            if f == 'chr':
                return f'chr({self.ch(["65", "97", "48", "0", "10", "255", self.expr(d, "num")])})'
            if f == 'sprintf':
                return self.sprintf(d)
            if f == 'join':
                return f'join({self.ch(["\",\"", "\"\"", "\"-\"", "\" \""])}, {self.listexpr(d)})'
            if f == 'reverse':
                return f'join("", reverse({self.listexpr(d)}))'
            r = self.vars('$', {'aref', 'href', 'sref', 'code'})
            return f'ref({self.ch(r) if r else self.anon(1)})'
        if k < 0.53:
            return self.side(d, 'str')
        if k < 0.63:
            e = self.elem(d)
            if e and self.p(0.6):
                e = f'({e} // {self.ch(["\"\"", "\"d\"", "0"])})'
            return e if e else self.leaf('str')
        if k < 0.70:
            return self.call(d, 'str')
        if k < 0.77:
            return self.ternary(d, 'str')
        if k < 0.82:
            return self.logic(d, 'str')
        if k < 0.88:
            return self.interp()
        if k < 0.91:
            return self.ch(["q{" + self.ch(['a b', 'x', '{n}', '']) + "}", "qq{" + self.ch(['a', 'b c', '']) + "}", "q(a)", "qq[z]"])
        return self.leaf('str')

    def sprintf(self, d):
        convs = []
        args = []
        for _ in range(self.r.randint(1, 3)):
            c = self.ch(['%s', '%d', '%5s', '%-4s|', '%03d', '%.2f', '%e', '%g', '%x', '%o', '%b', '%+d', '%5.1f', '%%', '%.3s', '%X', '%u', '%c', '%.0f', '%*d'])
            convs.append(c)
            if c == '%%':
                continue
            if c == '%*d':
                args.append(self.ch(['3', '-3', '0']))
            if c in ('%s', '%5s', '%-4s|', '%.3s'):
                args.append(self.expr(d, self.ch(['str', 'num'])))
            elif c == '%c':
                args.append(self.ch(['65', '97', '33']))
            else:
                args.append(self.expr(d, 'num'))
        if self.p(0.1) and args:
            args.pop()
        fmt = '"' + '<'.join(convs) + '"'
        return f'sprintf({fmt}' + ''.join(', ' + a for a in args) + ')'

    def e_bool(self, d):
        k = self.r.random()
        if k < 0.35:
            op = self.ch(['==', '!=', '<', '<=', '>', '>='])
            return self.br(f'{self.expr(d, "num")} {op} {self.expr(d, "num")}')
        if k < 0.5:
            op = self.ch(['eq', 'ne', 'lt', 'le', 'gt', 'ge'])
            return self.br(f'{self.expr(d, "str")} {op} {self.expr(d, "str")}')
        if k < 0.6:
            return self.br('!' + self.br(self.expr(d)))
        if k < 0.7:
            what = self.ch([self.expr(d), self.elem(d) or '1'])
            return f'defined({what})'
        if k < 0.78:
            h = self.vars('%')
            rh = self.vars('$', {'href'})
            if h and (not rh or self.p(0.5)):
                return f'exists(${self.ch(h)[1:]}{{{self.key(d)}}})'
            if rh:
                return f'exists({self.ch(rh)}->{{{self.key(d)}}})'
            return 'false'
        if k < 0.88:
            return self.logic(d, 'bool')
        if k < 0.92:
            r = self.vars('$', {'aref', 'href', 'code', 'sref'})
            if len(r) >= 1:
                return self.br(f'{self.ch(r)} {self.ch(["==", "!="])} {self.ch(r)}')
        return self.br(self.expr(d, self.ch(['num', 'str'])) + self.ch([' == ', ' eq ']) + self.expr(d, self.ch(['num', 'str'])))

    def e_ref(self, d):
        k = self.r.random()
        if k < 0.4:
            return self.anon(d)
        if k < 0.55:
            a = self.vars('@')
            h = self.vars('%')
            opts = [f'\\{x}' for x in a + h]
            if opts:
                return self.ch(opts)
        if k < 0.7:
            e = self.elem(d)
            if e:
                return e
        if k < 0.8:
            return self.anonsub(d)
        return self.leaf('ref')

    def logic(self, d, want):
        op = self.ch(['||', '&&', '//', 'or', 'and', 'xor'] if want == 'bool' else ['||', '&&', '//'])
        a = self.expr(d, want if self.p(0.6) else 'any')
        b = self.expr(d, want)
        if op == 'xor':
            a, b = self.expr(d, 'bool'), self.expr(d, 'bool')
        return self.br(f'{a} {op} {b}')

    def ternary(self, d, want):
        return self.br(f'{self.expr(d, "bool")} ? {self.expr(d, want)} : {self.expr(d, want)}')

    def blockexpr(self, d, want):
        """The expression of a map, a grep or a sort block, which sees $_."""
        self.topics.append(1)
        self.in_block_expr += 1
        try:
            if self.p(0.2):
                # a block that prints: what perl runs, and when, shows
                return f'print("b", (ref($_) ? "r" : $_ // "u"), " "); ' + self.blockexpr_(d, want)
            return self.blockexpr_(d, want)
        finally:
            self.topics.pop()
            self.in_block_expr -= 1

    def blockexpr_(self, d, want):
        if True:
            if want == 'num' and self.p(0.4):
                return self.br(f'$_ {self.ch(["+", "*", "-", "."])} {self.expr(min(d, 1), "num")}')
            if want == 'bool' and self.p(0.4):
                return self.br(f'$_ {self.ch([">", "<", "==", "ne", "eq"])} {self.expr(min(d, 1), "any")}')
            return self.expr(min(d, 2), want)

    def listexpr(self, d):
        """A list."""
        k = self.r.random()
        a = self.vars('@')
        if k < 0.2:
            return '(' + ', '.join(self.expr(max(d - 1, 0), self.ch(['num', 'str'])) for _ in range(self.r.randint(0, 4))) + ')'
        if k < 0.35 and a:
            return self.ch(a)
        if k < 0.42:
            lo = self.ch(['0', '1', '-2', '3'])
            hi = self.ch(['3', '5', '0', '2'] + [f'$#{x[1:]}' for x in a] + [self.ch(self.vars('$', {'int'}) or ['4'])])
            if self.p(0.1):
                lo = self.call(0, 'num')
            return f'({lo} .. {hi})'
        if k < 0.5 and a:
            x = self.ch(a)
            return self.ch([f'{x}[0, 1]', f'{x}[1 .. 2]', f'{x}[-1, 0]'])
        if k < 0.58:
            return f'(map {{ {self.blockexpr(d, self.ch(["num", "str"]))} }} {self.listexpr(d - 1) if d > 0 else "(1, 2, 3)"})'
        if k < 0.64:
            return f'(grep {{ {self.blockexpr(d, "bool")} }} {self.listexpr(d - 1) if d > 0 else "(1, 2, 3)"})'
        if k < 0.70:
            return self.sortexpr(d)
        if k < 0.74:
            h = self.vars('%')
            if h:
                hh = self.ch(h)
                return self.ch([f'(sort keys {hh})', f'(sort values {hh})', f'(sort {{ $a cmp $b }} keys {hh})', f'@{hh[1:]}{{"{self.ch(WORDS)}", "{self.ch(WORDS)}"}}'])
        if k < 0.80:
            r = self.vars('$', {'aref'})
            if r:
                x = self.ch(r)
                return self.ch([f'{x}->@*', f'@{{{x}}}', f'{x}->@[0, 1]', f'@{{{x}}}[0 .. 1]'[0:0] + f'{x}->@[1, 0]'])
            rh = self.vars('$', {'href'})
            if rh:
                x = self.ch(rh)
                return self.ch([f'(sort keys {x}->%*)', f'(sort keys %{{{x}}})', f'{x}->@{{"{self.ch(WORDS)}", "{self.ch(WORDS)}"}}'])
        if k < 0.86:
            return self.call(d, 'list')
        if k < 0.9:
            return self.ch(['qw(a b c)', 'qw[x y]', 'qw{1 2 3}', 'qw(0 1.5 3.0)'])
        if k < 0.94:
            return f'reverse({self.listexpr(max(d - 1, 0))})'
        if k < 0.97:
            return f'(({self.expr(0, "num")}, {self.expr(0, "str")}) x {self.ch(["2", "0", "1"])})'
        return '(' + ', '.join(self.expr(max(d - 1, 0)) for _ in range(self.r.randint(1, 3))) + ')'

    def sortexpr(self, d):
        inner = unbracket(self.listexpr(d - 1) if d > 0 else '(3, 1, 2)')
        k = self.r.random()
        if k < 0.3:
            return f'(sort {inner})'
        self.sortvars = True
        try:
            blk_ = self.ch(['$a <=> $b', '$b <=> $a', '$a cmp $b', '$b cmp $a', 'length($a) <=> length($b) || $a cmp $b',
                            f'{self.expr(1, "num")} <=> {self.expr(1, "num")}', '0', '$a <=> $b or $a cmp $b',
                            '0.5', '($a <=> $b) * 0.9', '"1"', '$b - $a', 'length($a) - length($b)', '-($a cmp $b)', '($a <=> $b) - 0.5',
                            f'{self.call(1, "num")} <=> 1 || $a cmp $b'])
        finally:
            self.sortvars = False
        if self.p(0.2):
            blk_ = 'print("c", ($a // "u"), ($b // "u"), " "); ' + blk_
        return f'(sort {{ {blk_} }} {inner})'

    def anonsub(self, d):
        if self.in_block_expr or self.in_anon > 1:
            return self.anon(1)
        params = self.params()
        self.in_anon += 1
        saved = (self.loop_labels, self.topics, self.sortvars)
        self.loop_labels, self.topics, self.sortvars = [], [], False
        self.push('sub')
        for p in params[1]:
            self.declare(p[0], kind=p[1])
        body = []
        for _ in range(self.r.randint(0, 2)):
            st = self.simple_stmt(max(d - 1, 0))
            if st:
                body.append(st)
        ret = self.expr(max(d - 1, 1), self.ch(['num', 'str']))
        self.pop()
        self.loop_labels, self.topics, self.sortvars = saved
        self.in_anon -= 1
        sig = '' if params[0] is None else '(' + params[0] + ')'
        inner = ' '.join(body + [f'return {ret};' if self.p(0.5) else ret])
        name = sig and ' ' + sig
        return f'sub{name} {{ {inner} }}'

    def params(self):
        if self.p(0.1):
            return (None, [])
        ps = []
        names = []
        n = self.r.randint(0, 3)
        opt = False
        for i in range(n):
            nm = f'$p{LETTERS[i]}'
            if opt or self.p(0.3):
                opt = True
                dflt = self.ch(['= 1', '//= "d"', '||= 2', '= undef', f'= {nm[:-1]}{LETTERS[i - 1]}' if i else '= 0', '= "s"'])
                ps.append(f'{nm} {dflt}')
            else:
                ps.append(nm)
            names.append((nm, 'any'))
        if self.p(0.2):
            if self.p(0.6):
                ps.append('@rest')
                names.append(('@rest', None))
            else:
                ps.append('%opts')
                names.append(('%opts', None))
        return (', '.join(ps), names)

    def call(self, d, want):
        opts = [n for n, s in self.subs.items() if s['ok'](self)]
        codes = self.vars('$', {'code'})
        if (not opts and not codes) or self.in_block_expr > 1:
            return self.leaf('num' if want == 'list' else want)
        args = lambda n: ', '.join(self.expr(max(d - 1, 0), self.ch(['num', 'str', 'any'])) if self.p(0.8) else (self.ch(self.vars('@')) if self.vars('@') else '1') for _ in range(n))
        if codes and (not opts or self.p(0.3)):
            c = self.ch(codes)
            info = self.scope.all()[c]
            n = self.r.randint(info.get('min', 0), info.get('max', 2))
            return f'{c}->({args(n)})'
        name = self.ch(opts)
        s = self.subs[name]
        n = self.r.randint(s['min'], s['max'] if s['max'] is not None else s['min'] + 2)
        if self.p(0.05):
            n += 1
        return f'{name}({args(n)})'

    # ---- statements
    def simple_stmt(self, d):
        """A statement of one line."""
        self.recent = []
        if self.p(0.12):
            t = self.template(d)
            if t:
                return t
        k = self.r.random()
        if k < 0.30:
            return self.assign_stmt(d)
        if k < 0.45:
            return self.say_stmt(d)
        if k < 0.52:
            pl = self.place(d, {'int', 'num', 'nstr', 'undef', 'bool'})
            if pl:
                return self.ch([f'{pl}++;', f'{pl}--;', f'++{pl};', f'--{pl};'])
        if k < 0.62:
            return self.array_stmt(d)
        if k < 0.70:
            return self.my_stmt(d)
        if k < 0.75:
            c = self.call(d, 'num')
            if '(' in c and not c.startswith('('):
                return c + ';'
        if k < 0.80:
            return self.hash_stmt(d)
        if k < 0.85:
            sc = [v for v in self.vars('$', {'str', 'nstr'}, writable=True) if not self.scope.all()[v].get('const')]
            if sc:
                return f'{self.ch(["chomp", "chop"])}({self.ch(sc)});'
        if k < 0.88:
            return f'printf({self.sprintf(d)[8:]};'.replace('printf((', 'printf(') if False else 'printf' + self.sprintf(d)[7:] + ';'
        st = self.assign_stmt(d)
        return st

    def template(self, d):
        """A shape known to stand where the orders and the aliases meet."""
        sc = [v for v in self.vars('$', {'int', 'num', 'str', 'nstr', 'bool'}, writable=True) if not self.scope.all()[v].get('const')]
        arr = self.vars('@')
        hs = self.vars('%')
        k = self.r.randrange(20)
        x = self.ch(sc) if sc else None
        e = lambda w='num': self.expr(1, w)
        if k == 0 and x:
            return self.ch([f'say({x}, ({x} = {e()}), {x});', f'say({x} + ({x} = {e()}));', f'say(({x} = {e()}) + {x}++);',
                            f'say({x}++ + {x}, {x}-- - {x});', f'say(({x} += 2) * ({x} -= 1));', f'say("{x[1:]}:", ({x} .= "s") . {x});'])
        if k == 1 and x and arr:
            a = self.ch(arr)
            return self.ch([f'${a[1:]}[{x} = {self.index(0)}] = {x};', f'${a[1:]}[{x}] = ({x} = {self.index(0)});',
                            f'${a[1:]}[{self.index(0)}] = {x} . ({x} = 1);', f'say(${a[1:]}[0] // "u", push({a}, {e()}), ${a[1:]}[-1] // "u");',
                            f'(${a[1:]}[0], ${a[1:]}[1]) = (${a[1:]}[1], ${a[1:]}[0]);', f'say(scalar({a}), ({a} = ({e()})), scalar({a}));'])
        if k == 2 and x and self.subs:
            f = self.ch(sorted(self.subs))
            return f'say(join(",", map {{ $_ // "u" }} {f}({x}, ({x} = {e()}), {x})));' if self.subs[f]['max'] is None or self.subs[f]['max'] >= 3 else None
        if k == 3 and x and hs:
            h = self.ch(hs)
            return self.ch([f'${h[1:]}{{{x}}} = ({x} = "k");', f'${h[1:]}{{{x} = "a"}} = {x};', f'say(exists(${h[1:]}{{k}}) ? 1 : 0, delete(${h[1:]}{{k}}) // "u", exists(${h[1:]}{{k}}) ? 1 : 0);'])
        if k == 4 and arr:
            a = self.ch(arr)
            r = self.fresh('$v')
            self.declare(r, kind='aref')
            return f'my {r} = \\{a}; push({a}, {e()}); {r}->[0] = {e()}; say(${a[1:]}[0], scalar({r}->@*), ${a[1:]}[-1] // "u");'
        if k == 5:
            c = self.fresh('@l')
            i = self.fresh('$e')
            o = x or '$v0'
            if not x:
                return None
            self.declare(c)
            return (f'my {c}; for my {i} (1 .. 3) {{ push({c}, sub {{ {i} . "/" . {o} }}); }} {o} = {e()}; '
                    f'say(join(",", map {{ $_->() }} {c}));')
        if k == 6 and arr:
            a = self.ch(arr)
            n = self.fresh('$v')
            self.declare(n, kind='int')
            return f'my {n} = 0; say(join(",", sort {{ {n}++; ($a // 0) <=> ($b // 0) }} grep {{ !ref($_) }} {a}), " ", {n});'
        if k == 7 and len(sc) >= 2:
            y, z = self.r.sample(sc, 2)
            return self.ch([f'({y}, {z}) = ({z}, {y});', f'({y}, {z}) = ({z}, {y} . {z});', f'({y}, {z}) = ({z} + 1, {y} + {z});'])
        if k == 8 and x:
            r = self.fresh('$v')
            self.declare(r, kind='sref')
            return f'my {r} = \\{x}; {r}->$* = {e()}; say({x}, " ", ${{{r}}} + ({x} = 1), " ", {x});'
        if k == 9 and x:
            f = self.fresh('$f')
            self.declare(f, kind='code', const=True, min=0, max=0)
            return f'my {f} = sub () {{ {x} = {x} . "c"; return {x}; }}; say({x}, {f}->(), {x}, {f}->() . {x});'
        if k == 10:
            v = self.fresh('$v')
            self.declare(v, kind='num')
            n = self.ch(['9007199254740991', '9007199254740992', '9223372036854775806', '-9223372036854775807', '4503599627370496.5', '1e15', '999999999999999', '"9007199254740991"', '"3.0"', '0.5', '-0.0', '"-0.0"'])
            return f'my {v} = {n}; {v}++; say({v}, " ", {v} + 1, " ", {v} * 2, " ", {v} / 2, " ", -{v});'
        if k == 11 and arr:
            a = self.ch(arr)
            return self.ch([f'for my $q (0 .. 1) {{ say(${a[1:]}[$q] // "u"); }}', f'say(join("|", map {{ $_ // "u" }} {a}[0, 1, 2]), " ", scalar({a}));',
                            f'say(join(",", map {{ ref($_) ? "r" : $_ // "u" }} reverse({a})));',
                            f'say(join(",", map {{ ref($_) eq "CODE" ? $_->() // "u" : "n" }} {a}));'])
        if k == 12 and x:
            return self.ch([f'say(({x} ||= {e()}) . ({x} //= 5) . ({x} &&= {e()}));', f'say({x} x 2, {x} x 0, "-" x 3);',
                            f'say(sprintf("%s|%d|%.3g|%5.1f", {x}, length({x}), 2.5, 7));'])
        if k == 13 and x:
            return f'try {{ {x} = {e()}; die("d:" . {x} . "\\n"); }} catch ($er) {{ print($er); {x} = {e()}; }}'
        if k == 14:
            body = '\n'.join(self.ch(['line', 'two  words', '', 'x']) + (self.interp()[1:-1] if self.p(0.6) else '') for _ in range(self.r.randint(1, 3)))
            q = self.ch(['"END"', 'END', "'END'"])
            if q == "'END'":
                body = body.replace('$', '').replace('@', '')
            return f'print(<<~{q});\n{body}\nEND'
        if k == 15:
            return f'warn("w", {e(self.ch(["num", "str"]))}, "\\n");'
        if k == 16:
            c = self.fresh('$v')
            self.declare(c, kind='int')
            n = self.ch(['0', '2', '5'])
            return self.ch([f'my {c} = 0; {c}++ while {c} < {n}; say({c});', f'my {c} = 9; {c}-- until {c} <= {n}; say({c});'])
        if k == 17:
            f = self.fresh('$f')
            self.declare(f, kind='code', const=True, min=1, max=1)
            return f'my {f} = sub ($n) {{ return $n <= 1 ? {e()} : $n . __SUB__->($n - 1); }}; say({f}->({self.ch(["0", "3", "5"])}));'
        if k == 18 and hs:
            h = self.ch(hs)
            g = self.fresh('%h')
            self.declare(g)
            return f'my {g} = (%{h[1:]}, {self.ch(WORDS)} => {e()}); say(join(",", map {{ $_ . "=" . (ref(${g[1:]}{{$_}}) ? "r" : ${g[1:]}{{$_}} // "u") }} sort keys {g}), " ", scalar(%{g[1:]}));'
        if k == 19 and self.vars('$', {'href', 'aref'}):
            r = self.ch(self.vars('$', {'href', 'aref'}))
            if self.scope.all()[r]['kind'] == 'href':
                return f'say(join(",", sort keys {r}->%*), " ", scalar(%{{{r}}}), " ", join(",", map {{ ref($_) ? "r" : $_ // "u" }} @{{{r}}}{{"k", "a"}}));'
            return f'say(scalar({r}->@*), " ", $#{{{r}}}, " ", join(",", map {{ ref($_) ? "r" : $_ // "u" }} {r}->@[0, -1]));'
        return None

    def modifier(self, st, d):
        if st and st.endswith(';') and self.p(0.15) and not st.startswith('my ') and ' if ' not in st and ' unless ' not in st and ' for ' not in st:
            m = self.ch(['if', 'unless'])
            return st[:-1] + f' {m} {self.expr(min(d, 2), "bool")};'
        return st

    def say_stmt(self, d):
        items = []
        for _ in range(self.r.randint(1, 3)):
            k = self.r.random()
            if k < 0.6:
                items.append(self.expr(d, self.ch(['num', 'str', 'str', 'bool'])))
            elif k < 0.85:
                items.append(self.listexpr(d))
            else:
                items.append(self.dump_expr())
        word = self.ch(['say', 'say', 'print'])
        tail = ', "\\n"' if word == 'print' else ''
        if self.p(0.04):
            return f'{word} STDERR ' + f'"w", ' + ', '.join(items) + tail + ';'
        return f'{word}(' + self.ch(['', '"> ", ']) + ', '.join(items) + tail + ');'

    def dump_expr(self):
        """A value printed so that nothing in it faults."""
        sc = self.vars('$')
        a = self.vars('@')
        h = self.vars('%')
        k = self.r.random()
        safe = lambda e: f'(defined({e}) ? (ref({e}) ? ref({e}) : {e}) : "u")'
        if k < 0.4 and sc:
            v = self.ch(sc)
            return safe(v)
        if k < 0.7 and a:
            x = self.ch(a)
            return f'join(",", map {{ {safe("$_")} }} {x})'
        if h:
            x = self.ch(h)
            return f'join(",", map {{ $_ . "=" . {safe("$" + x[1:] + "{$_}")} }} sort keys {x})'
        return '"."'

    def value_kind(self, e, want):
        return {'num': 'num', 'str': 'str', 'bool': 'bool'}.get(want, 'any')

    def assign_stmt(self, d):
        k = self.r.random()
        if k < 0.15:
            # a list assignment
            sc = [v for v in self.vars('$', writable=True) if not self.scope.all()[v].get('const')]
            if len(sc) >= 2:
                xs = self.r.sample(sc, 2)
                tgt = ', '.join(xs)
                if self.p(0.3) and self.vars('@'):
                    tgt += ', ' + self.ch(self.vars('@'))
                return f'({tgt}) = {self.ch([self.listexpr(d), "(" + ", ".join(reversed(xs)) + ")"])};'
        if k < 0.22:
            a = self.vars('@')
            if a:
                x = self.ch(a)
                if self.p(0.3):
                    return f'{x}[{self.index(0)}, {self.index(0)}] = {self.listexpr(d)};'
                return f'{x} = {self.listexpr(d)};'
        if k < 0.27:
            h = self.vars('%')
            if h:
                x = self.ch(h)
                if self.p(0.4):
                    return f'@{x[1:]}{{"{self.ch(WORDS)}", "{self.ch(WORDS)}"}} = {self.listexpr(d)};'
                return f'{x} = ({self.pairs(d)});'
        want = self.ch(['num', 'num', 'str', 'str', 'bool', 'ref'])
        pl = self.place(d)
        if pl is None:
            return self.my_stmt(d)
        op = self.ch(['=', '=', '=', '+=', '-=', '.=', '*=', '||=', '//=', '&&=', '/=', '%=', '**=', 'x='])
        if op in ('+=', '-=', '*=', '/=', '%=', '**='):
            want = 'num'
        if op == '.=':
            want = 'str'
        rhs = self.expr(d, want)
        if op == 'x=':
            rhs = self.ch(['0', '1', '2', '3'])
        if op == '**=':
            rhs = self.ch(['2', '0', '3', '0.5', '-1'])
        info = self.scope.all().get(pl)
        if info is not None and op == '=':
            info['kind'] = self.kind_of(want, rhs)
        return self.modifier(f'{pl} {op} {rhs};', d)

    def kind_of(self, want, rhs):
        if want == 'ref':
            if rhs.startswith('['):
                return 'aref'
            if rhs.startswith('{'):
                return 'href'
            if rhs.startswith('\\@'):
                return 'aref'
            if rhs.startswith('\\%'):
                return 'href'
            if rhs.startswith('\\$'):
                return 'sref'
            if rhs.startswith('sub'):
                return 'any'   # never called: a code var is assigned once (T131)
            return 'any'
        return {'num': 'num', 'str': 'str', 'bool': 'bool'}[want]

    def pairs(self, d):
        return ', '.join(f'{self.ch(WORDS)} => {self.expr(max(d - 1, 0), self.ch(["num", "str", "ref"]))}' for _ in range(self.r.randint(0, 4)))

    def my_stmt(self, d):
        k = self.r.random()
        if k < 0.45:
            want = self.ch(['num', 'num', 'str', 'str', 'bool', 'ref', 'ref', 'nstr'])
            name = self.fresh('$v')
            if want == 'nstr':
                rhs = self.ch(NSTRS)
                kind = 'nstr' if NSTRS.index(rhs) < 18 else 'str'
            elif want == 'ref':
                rhs = self.ch([self.anon(d), self.anon(d), self.e_ref(d)])
                kind = self.kind_of('ref', rhs)
            else:
                rhs = self.expr(d, want)
                kind = self.kind_of(want, rhs)
            st = f'my {name} = {rhs};'
            self.declare(name, kind=kind)
            return st
        if k < 0.55:
            name = self.fresh('$v')
            self.declare(name, kind='undef')
            return f'my {name};'
        if k < 0.72:
            name = self.fresh('@l')
            st = f'my {name} = {self.listexpr(d)};'
            self.declare(name)
            return st
        if k < 0.85:
            name = self.fresh('%h')
            st = f'my {name} = ({self.pairs(d)});'
            self.declare(name)
            return st
        if k < 0.92:
            a, b = self.fresh('$v'), self.fresh('$v')
            rest = ''
            if self.p(0.3):
                r = self.fresh('@l')
                rest = ', ' + r
            st = f'my ({a}, {b}{rest}) = {self.listexpr(d)};'
            self.declare(a, kind='any')
            self.declare(b, kind='any')
            if rest:
                self.declare(rest[2:])
            return st
        # a closure, assigned once and never again (T131: no call cycle)
        name = self.fresh('$f')
        sub = self.anonsub(d)
        if not sub.startswith('sub'):
            st = f'my {name} = {sub};'
            self.declare(name, kind=self.kind_of('ref', sub))
            return st
        st = f'my {name} = {sub};'
        mn, mx = sig_arity(sub)
        self.declare(name, kind='code', const=True, min=mn, max=mx)
        return st

    def array_stmt(self, d):
        a = self.vars('@')
        r = self.vars('$', {'aref'})
        if not a and not r:
            return self.my_stmt(d)
        tgt = self.ch(a) if a and (not r or self.p(0.6)) else self.ch([f'{self.ch(r)}->@*', f'@{{{self.ch(r)}}}'])
        k = self.ch(['push', 'push', 'unshift', 'pop', 'shift', 'splice', 'splice2', 'pushret'])
        if k in ('push', 'unshift'):
            return f'{k}({tgt}, {self.listexpr(d) if self.p(0.4) else self.expr(d, self.ch(["num", "str", "ref"]))});'
        if k == 'pop':
            return f'pop({tgt});'
        if k == 'shift':
            return f'shift({tgt});'
        if k == 'splice':
            return f'splice({tgt}, {self.ch(["0", "1", "-1"])}, {self.ch(["0", "1", "2"])}, {self.expr(d, "num")});'
        if k == 'splice2':
            n = self.fresh('@l')
            st = f'my {n} = splice({tgt}, {self.ch(["0", "1", "-1"])});'
            self.declare(n)
            return st
        sc = [v for v in self.vars('$', writable=True) if not self.scope.all()[v].get('const')]
        if sc:
            v = self.ch(sc)
            self.scope.all()[v]['kind'] = 'int'
            return f'{v} = {self.ch(["push", "unshift"])}({tgt}, {self.expr(d, "num")});'
        return f'push({tgt}, 1);'

    def hash_stmt(self, d):
        h = self.vars('%')
        rh = self.vars('$', {'href'})
        if not h and not rh:
            return self.my_stmt(d)
        if h and (not rh or self.p(0.6)):
            x = self.ch(h)
            k = self.r.random()
            if k < 0.4:
                return f'delete ${x[1:]}{{{self.key(d)}}};'
            if k < 0.6:
                n = self.fresh('@l')
                self.declare(n)
                return f'my {n} = delete @{x[1:]}{{"{self.ch(WORDS)}", "{self.ch(WORDS)}"}};'
            return f'${x[1:]}{{{self.key(d)}}} = {self.expr(d)};'
        x = self.ch(rh)
        if self.p(0.5):
            return f'delete {x}->{{{self.key(d)}}};'
        return f'{x}->{{{self.key(d)}}} = {self.expr(d)};'

    # ---- compound statements
    def stmt(self, d, top=False):
        k = self.r.random()
        if d <= 0 or k < 0.55:
            st = self.simple_stmt(d)
            return [self.modifier(st, d)] if st else None
        if k < 0.63:
            return self.if_stmt(d)
        if k < 0.70:
            return self.cfor(d)
        if k < 0.80:
            return self.foreach(d)
        if k < 0.84:
            return self.while_stmt(d)
        if k < 0.89:
            return self.try_stmt(d)
        if k < 0.92:
            return self.bare_block(d)
        if k < 0.96:
            return self.stmt_for(d)
        if self.loop_labels and self.p(0.7):
            return [self.jump(d)]
        st = self.simple_stmt(d)
        return [st] if st else None

    def jump(self, d):
        w = self.ch(['last', 'next'])
        labs = [l for l in self.loop_labels if l and l != 'BARE']
        target = f' {self.ch(labs)}' if labs and self.p(0.6) else ''
        if not target and self.loop_labels[-1] == 'BARE':
            labs = [l for l in self.loop_labels if l]
            return 'say("nj");'
        return f'{w}{target} if {self.expr(1, "bool")};'

    def block(self, d, n=None, need=False):
        self.push()
        stmts = []
        for _ in range(n if n is not None else self.r.randint(1, 4)):
            s = self.stmt(d - 1)
            if s:
                stmts.append(s)
        self.pop()
        return blk(stmts, need)

    def if_stmt(self, d):
        parts = [f'if ({self.test(d)}) {{\n', self.block(d), '}']
        for _ in range(self.r.randint(0, 2) if self.p(0.4) else 0):
            parts += [f' elsif ({self.test(d)}) {{\n', self.block(d), '}']
        if self.p(0.4):
            parts += [' else {\n', self.block(d), '}']
        if self.p(0.1):
            return [f'unless ({self.test(d)}) {{\n', self.block(d), '}']
        return parts

    def test(self, d):
        if self.p(0.1):
            sc = [v for v in self.vars('$', writable=True) if not self.scope.all()[v].get('const')]
            if sc:
                return f'({self.ch(sc)} = {self.expr(1, "num")})'
        return self.expr(min(d, 2), 'bool')

    def label(self):
        if self.p(0.3):
            return self.ch(['OUTER', 'INNER', 'L1', 'ROW']) + ': '
        return ''

    def loop_body(self, d, lab):
        self.loop_labels.append(lab[:-2] if lab else None)
        self.depth_loops += 1
        b = self.block(d)
        if self.p(0.4):
            b['stmts'].insert(self.r.randint(0, len(b['stmts'])), [self.jump(d)])
        self.depth_loops -= 1
        self.loop_labels.pop()
        return b

    def cfor(self, d):
        if self.depth_loops >= 2:
            return [self.simple_stmt(d)]
        i = self.fresh('$i')
        lab = self.label()
        n = self.ch(['0', '1', '3', '4'])
        self.push()
        self.declare(i, kind='int', ro=True)
        body = self.loop_body(d, lab)
        self.pop()
        return [f'{lab}for (my {i} = 0; {i} < {n}; {i}++) {{\n', body, '}']

    def while_stmt(self, d):
        if self.depth_loops >= 2:
            return [self.simple_stmt(d)]
        w = self.fresh('$w')
        lab = self.label()
        n = self.ch(['0', '2', '3'])
        self.declare(w, kind='int', ro=True)
        word = self.ch(['while', 'until'])
        test = f'{w}++ < {n}' if word == 'while' else f'{w}++ >= {n}'
        body = self.loop_body(d, lab)
        return [f'my {w} = 0;\n{lab}{word} ({test}) {{\n', body, '}']

    def foreach(self, d):
        if self.depth_loops >= 2:
            return [self.simple_stmt(d)]
        lab = self.label()
        lst = self.listexpr(max(d - 1, 0))
        k = self.r.random()
        if k < 0.25:
            # $_
            self.push()
            self.topics.append(1)
            body = self.loop_body(d, lab)
            self.topics.pop()
            self.pop()
            return [f'{lab}for ({lst}) {{\n', body, '}']
        x = self.fresh('$e')
        self.push()
        self.declare(x, kind='any', ro=True, loopvar=True)
        body = self.loop_body(d, lab)
        # a closure over the loop's variable, kept for later (D162)
        if self.p(0.3) and self.vars('@'):
            a = self.ch(self.vars('@'))
            body['stmts'].append([f'push({a}, sub {{ {x} }});'])
        self.pop()
        word = self.ch(['for', 'foreach'])
        return [f'{lab}{word} my {x} ({lst}) {{\n', body, '}']

    def stmt_for(self, d):
        self.topics.append(1)
        st = self.ch([lambda: f'say({self.blockexpr(1, self.ch(["num", "str"]))})',
                      lambda: f'{self.place(1) or "my $zz"} .= $_'])()
        self.topics.pop()
        return [f'{st} for {self.listexpr(max(d - 1, 0))};']

    def try_stmt(self, d):
        e = self.fresh('$err')
        tb = self.block(d)
        if self.p(0.7):
            tb['stmts'].insert(self.r.randint(0, len(tb['stmts'])), [self.die_stmt(d)])
        self.push()
        self.declare(e, kind='str')
        cb = self.block(d)
        cb['stmts'].insert(0, [f'say("caught: ", ref({e}) ? ref({e}) : {e});' if self.p(0.7) else f'print("caught ", {e});'])
        self.pop()
        return ['try {\n', tb, f'}}\ncatch ({e}) {{\n', cb, '}']

    def die_stmt(self, d):
        k = self.r.random()
        msg = self.expr(min(d, 1), self.ch(['str', 'num']))
        if k < 0.4:
            return f'die({msg}, "\\n") if {self.expr(1, "bool")};'
        if k < 0.6:
            return f'die {self.anon(1)};'
        if k < 0.8:
            return f'die({msg});'
        return f'die "x" . {msg} . "\\n";'

    def bare_block(self, d):
        self.loop_labels.append('BARE')
        b = self.block(d, need=True)
        self.loop_labels.pop()
        return ['{\n', b, '}']

    def sub_def(self, i):
        name = f'fn{LETTERS[i]}'
        params = self.params()
        self.push('sub')
        saved = (self.loop_labels, self.topics)
        self.loop_labels, self.topics = [], []
        for p in params[1]:
            self.declare(p[0], kind=p[1] if p[1] else None)
        body = self.block(3, self.r.randint(1, 4))
        if self.p(0.3):
            # a die that goes through whoever called: a map, a sort, a loop
            body['stmts'].insert(self.r.randint(0, len(body['stmts'])), [self.die_stmt(1)])
        # an ending: return a value, a list, nothing, or a last expression
        k = self.r.random()
        lst = False
        self.push()
        if k < 0.35:
            body['stmts'].append([f'return {self.expr(2, self.ch(["num", "str"]))};'])
        elif k < 0.5:
            body['stmts'].append([f'return {self.listexpr(2)};'])
            lst = True
        elif k < 0.6:
            body['stmts'].append(['return;'])
        elif k < 0.85:
            body['stmts'].append([self.expr(2, self.ch(['num', 'str'])) + ';'])
        else:
            body['stmts'].append([f'return {self.expr(1, "num")} if {self.expr(1, "bool")};'])
        self.pop()
        self.loop_labels, self.topics = saved
        self.pop()
        sig = '' if params[0] is None else f'({params[0]})'
        mn, mx = arity(params)
        # a sub may call only the subs before it: no cycle (T131)
        self.subs[name] = {'min': mn, 'max': mx, 'list': lst, 'ok': (lambda g, name=name: g.in_sub is None or g.in_sub > name)}
        return [f'sub {name}{sig} {{\n', body, '}']

    def program(self):
        top = blk()
        nsubs = self.r.randint(0, 4) if not self.dense else self.r.randint(0, 1)
        # the file's variables first, so that subs may see them
        ndecl = self.r.randint(2, 5)
        for _ in range(ndecl):
            top['stmts'].append([self.my_stmt(2)])
        subs = []
        for i in range(nsubs):
            self.in_sub = f'fn{LETTERS[i]}'
            subs.append(self.sub_def(i))
        self.in_sub = None
        for _ in range(self.r.randint(4, 14) if not self.dense else self.r.randint(25, 45)):
            s = self.stmt(3, top=True) if not self.dense else [self.simple_stmt(3)]
            if s:
                top['stmts'].append(s)
            if self.p(0.3):
                top['stmts'].append([self.say_stmt(1)])
            if self.p(0.25):
                top['stmts'].append([f'say({self.dump_expr()});'])
        # subs among the statements, where perl lets them stand
        for s in subs:
            top['stmts'].insert(self.r.randint(ndecl, len(top['stmts'])), s)
        # the last word: every variable, in a form that cannot fault
        for v in self.vars('$')[:6] + self.vars('@')[:3] + self.vars('%')[:3]:
            top['stmts'].append([f'say({dump(v)});'])
        head = 'use v5.42;\n'
        if self.needs_utf8:
            head += "use utf8;\nuse open ':std', ':encoding(UTF-8)';\n"
        if self.p(0.2):
            head += "no warnings 'recursion';\n"
        return head, top


def unbracket(s):
    """A list without the brackets round it, where they would be sort's own."""
    if not s.startswith('('):
        return s
    depth = 0
    for i, c in enumerate(s):
        depth += c == '('
        depth -= c == ')'
        if depth == 0:
            if i == len(s) - 1 and s[1:-1].strip():
                inner = s[1:-1]
                return '+' + inner if inner.startswith('$') else inner
            return s
    return s


class Ctx:
    """A program about context alone: subs whose values are what perl
    works out differently for a list, one value and nothing (D18, D245),
    each called in every context there is, directly, through a
    reference and handed on by another sub."""
    def __init__(self, r):
        self.r = r

    def value(self, d=2):
        r = self.r
        k = r.randrange(16)
        p = lambda: f'p({r.choice(["1", "2", "0", "3"])})'
        if d <= 0 or k < 2:
            return r.choice(['1', '"s"', '$n', p(), '@arr', '(1, 2)', '()', '(undef)'])
        if k == 2:
            return f'({p()} .. {r.choice(["2", "$n", p()])})'
        if k == 3:
            return f'sort {{ print("c "); $a <=> $b }} ({p()}, {p()}, 1)'
        if k == 4:
            return f'sort 3, {p()}'
        if k == 5:
            return f'map {{ print("m "); $_ }} {self.value(d - 1)}'
        if k == 6:
            return f'grep {{ print("g "); $_ }} ({p()}, 0, 4)'
        if k == 7:
            return f'reverse({self.value(d - 1)})'
        if k == 8:
            return f'({p()}, 5) x {r.choice(["0", "1", "2"])}'
        if k == 9:
            return f'$c ? {self.value(d - 1)} : {self.value(d - 1)}'
        if k == 10:
            return f'$c {r.choice(["||", "&&", "//"])} {self.value(d - 1)}'
        if k == 11:
            return f'({self.value(d - 1)}, {self.value(d - 1)})'
        if k == 12:
            return f'@arr[0, {r.choice(["1", "5", "-1"])}]'
        if k == 13:
            return f'({self.value(d - 1)})[{r.choice(["0", "1", "-1", "0, 1"])}]'
        if k == 14:
            return f'+({self.value(d - 1)})'
        return r.choice(['inner($c)', '$ref->($c)', '%hh', 'keys %hh'])

    def program(self):
        r = self.r
        body = ['my @arr = (3, 4);', 'my %hh = (k => 1);', 'my $n = 2;',
                'sub p($v) { print("p$v "); return $v }']
        # each sub's value on a line of its own, so that what a fault or a
        # refusal there takes out is the value, and not the sub
        subs = [['sub inner($c) {\n', blk([[f'return {self.value(1)};']]), '}'],
                ['my $ref = sub ($c) {\n', blk([[f'{self.value(1)}']]), '};']]
        nsubs = r.randint(2, 5)
        for i in range(nsubs):
            if r.random() < 0.7:
                subs.append([f'sub s{i}($c) {{\n', blk([[f'return {self.value()};']]), '}'])
            else:
                subs.append([f'sub s{i}($c) {{\n', blk([[f'say("in s{i}");'], [f'{self.value()}']]), '}'])
        stmts = []
        for _ in range(r.randint(10, 25)):
            f = f's{r.randrange(nsubs)}({r.choice(["0", "1"])})'
            if r.random() < 0.2:
                f = f'$ref->({r.choice(["0", "1"])})'
            k = r.randrange(12)
            stmts.append([
                f'{f}; say("void");',
                f'my @l{_} = {f}; say("list ", scalar(@l{_}));',
                f'my $x{_} = {f}; say("one ", $x{_} // "u");',
                f'say("say ", {f});',
                f'if ({f}) {{ say("true") }} else {{ say("false") }}',
                f'{f} for 1 .. 2; say("for");',
                f'say("args ", join(",", map {{ $_ // "u" }} {f}));',
                f'say("count ", scalar(@{{[{f}]}}));',
                f'my $t{_} = sub {{ return {f} }}; $t{_}->(); say("handed");',
                f'say("each ", join(",", map {{ $_ // "u" }} ({f}, {f})));',
                f'{f} if 1; say("if");',
                f'try {{ {f}; }} catch ($e) {{ }} say("try");',
            ][k])
        top = blk([[b] for b in body] + subs + stmts)
        return 'use v5.42;\n', top


def dump(v):
    safe = lambda e: f'(defined({e}) ? (ref({e}) ? ref({e}) : {e}) : "u")'
    if v[0] == '$':
        return f'"{v[1:]}=", {safe(v)}'
    if v[0] == '@':
        return f'"{v[1:]}=", join(",", map {{ {safe("$_")} }} {v})'
    return f'"{v[1:]}=", join(",", map {{ $_ . "=" . {safe("$" + v[1:] + "{$_}")} }} sort keys {v})'


def arity(params):
    if params[0] is None:
        return 0, 3
    names = params[1]
    mn = 0
    for p in params[0].split(', '):
        if p and p[0] == '$' and '=' not in p:
            mn += 1
    slurpy = any(n[0][0] in '@%' for n in names)
    mx = None if slurpy else len([n for n in names])
    return mn, (mx if mx is not None else mn + 2)


def sig_arity(sub):
    if not sub.startswith('sub ('):
        return 0, 2
    sig = sub[5:sub.index(')')]
    parts = [p for p in sig.split(', ') if p]
    mn = len([p for p in parts if p[0] == '$' and '=' not in p])
    if any(p[0] in '@%' for p in parts):
        return mn, mn + 2
    return mn, len(parts)


# ---- the tree

def render(head, top):
    """The program's text, and for each statement (by id) the lines it
    covers."""
    out = [head]
    ranges = {}
    line = [head.count('\n') + 1]

    def emit(text):
        out.append(text)
        line[0] += text.count('\n')

    def block(b, indent):
        for st in b['stmts']:
            start = line[0]
            emit(indent)
            for part in st:
                if isinstance(part, str):
                    emit(part.replace('\n', '\n' + indent) if not part.endswith('{\n') else part[:-1].replace('\n', '\n' + indent) + '\n')
                else:
                    block(part, indent + '    ')
                    emit(indent)
            emit('\n')
            ranges[id(st)] = (start, line[0] - 1, st, b)
    block(top, '')
    return ''.join(out), ranges


def delete_at(top, ranges, line):
    """Take out the innermost statement that covers the line; True if
    there was one."""
    best = None
    for start, end, st, b in ranges.values():
        if start <= line <= end and (best is None or end - start < best[1] - best[0]):
            best = (start, end, st, b)
    if best is None:
        return False
    _, _, st, b = best
    if len(st) == 1 and isinstance(st[0], str) and st[0].startswith('my ') and not st[0].startswith('my $w'):
        # a declaration: kept, with a value nothing can refuse, so that
        # what uses it later is not refused in turn
        safe = []
        for name in re.findall(r'[$@%]\w+', st[0].split('=')[0]):
            safe.append({'$': f'my {name} = 1;', '@': f'my {name} = (1, 2);', '%': f'my {name} = (k => 1);'}[name[0]])
        if safe and ' '.join(safe) != st[0]:
            st[0] = ' '.join(safe)
            return True
    b['stmts'] = [s for s in b['stmts'] if s is not st]
    if b['need'] and not b['stmts']:
        # a bare block may not be empty: take out what holds it
        for start, end, st2, b2 in ranges.values():
            if any(p is b for p in st2 if isinstance(p, dict)):
                b2['stmts'] = [s for s in b2['stmts'] if s is not st2]
                break
    return True


def generate(seed):
    if seed % 8 == 7:
        return Ctx(random.Random(seed)).program()
    return Gen(seed).program()


if __name__ == '__main__':
    head, top = generate(int(sys.argv[1]))
    print(render(head, top)[0], end='')
