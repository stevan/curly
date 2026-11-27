#!/usr/bin/env python3
"""t/4400 to t/4402, t/4500, t/4501 and t/4600: the numeric builtins, the
bit operators and perl's generator (step 22; D200 to D207).

The definition, which is all this file knows of them:

  int N        an Int is itself; a Num from -2^63 to 2^63, both left
               out, the Int it cuts to; past 2^64 or at -2^63 and below,
               itself (from 2^63 to 2^64 a fault, not written here)
  abs N        an Int's magnitude; an integral Num's (whole, below 2^53)
               the Int; any other Num's the Num, and a string with a point
               and no exponent is a Num here, whole or not (T487)
  sqrt sin cos exp log atan2
               a Num: C's function of the double, which Python's math
               module calls
  hex S, oct S S made a string as `.` makes one; perl's prefixes, the
               digits of the base with one `_` before the first or
               between two; no digits is 0
  & | ^ ~      each operand cut toward zero, as its 64 bits; the answer
               those 64 bits unsigned, written only below 2^63
  << >>        the same, a negative count the other way, 64 or more 0
  rand srand   FreeBSD's drand48 as perl carries it: the state 0x330E +
               (seed << 16), then x * 0x5DEECE66D + 0xB mod 2^48, and a
               value of x / 2^48 times the argument (0 meaning 1)

A Num prints as C's %.15g, a zero of either sign as 0; a model writes no
whole Num from 10^15 to 2^53, which faults (D36). perl is the second
derivation (t/checks.py oracle).

4400 is int and abs; 4401 the float functions; 4402 hex and oct; 4500 the
bit operators; 4501 the shifts and the assigning forms; 4600 rand and
srand.

Every command that writes a file, one a line (t/checks.py runs them all):

    python3 t/models/numfn.py --program 4400 > t/4400-int-abs.pl
    python3 t/models/numfn.py 4400 > t/4400-int-abs.expected
    python3 t/models/numfn.py --program 4401 > t/4401-float-functions.pl
    python3 t/models/numfn.py 4401 > t/4401-float-functions.expected
    python3 t/models/numfn.py --program 4402 > t/4402-hex-oct.pl
    python3 t/models/numfn.py 4402 > t/4402-hex-oct.expected
    python3 t/models/numfn.py --program 4500 > t/4500-bit-operators.pl
    python3 t/models/numfn.py 4500 > t/4500-bit-operators.expected
    python3 t/models/numfn.py --program 4501 > t/4501-shifts.pl
    python3 t/models/numfn.py 4501 > t/4501-shifts.expected
    python3 t/models/numfn.py --program 4600 > t/4600-rand-srand.pl
    python3 t/models/numfn.py 4600 > t/4600-rand-srand.expected
"""

import math
import random
import struct
import sys

TWO_53 = 2 ** 53
TWO_63 = 2 ** 63
TWO_64 = 2 ** 64


class Num(float):
    """A Num, as against a Python int, which is an Int."""


def show(v):
    if isinstance(v, Num):
        x = float(v)
        assert math.isfinite(x)
        assert not (x == math.trunc(x) and 1e15 <= abs(x) < TWO_53), x
        return '0' if x == 0 else '%.15g' % x
    return str(v)


def lit(v):
    """A literal the language reads as this value, Int or Num."""
    if isinstance(v, Num):
        x = float(v)
        r = repr(x)
        if 'e' in r or 'E' in r:
            mant, _, exp = r.partition('e')
            if '.' not in mant:
                mant += '.0'
            r = f'{mant}e{exp}'
        return f'({r})' if x < 0 else r
    return f'({v})' if v < 0 else str(v)


def int_of(v):
    if not isinstance(v, Num):
        return v
    x = float(v)
    assert not (TWO_63 <= x < TWO_64)
    if -TWO_63 < x < TWO_63:
        return int(math.trunc(x))
    return Num(x)


def integral(v):
    return not isinstance(v, Num) or (float(v) == math.trunc(float(v)) and abs(float(v)) < TWO_53)


def abs_of(v):
    if not isinstance(v, Num):
        assert v != -TWO_63
        return abs(v)
    if integral(v):
        return abs(int(float(v)))
    return Num(abs(float(v)))


def case_int_abs(rnd):
    values = [0, 7, -7, TWO_63 - 1, -TWO_63 + 1, Num(3.7), Num(-3.7), Num(0.5), Num(-0.5), Num(-0.0), Num(1e17), Num(-1e17),
              Num(9.2e18), Num(-9.2e18), Num(-9223372036854775808.0), Num(1.8446744073709552e19), Num(1e20), Num(-1e20),
              Num(1e15 + 0.5), Num(-1e15), Num(2.0 ** 53), Num(-2.0 ** 60), Num(123456789.987), Num(1e-300), Num(-1e300)]
    for _ in range(40):
        e = rnd.randint(-5, 25)
        values.append(Num(rnd.choice([1, -1]) * rnd.random() * 10 ** e))
    for _ in range(20):
        values.append(rnd.randint(-TWO_63 + 1, TWO_63 - 1))
    lines, out = [], []
    for v in values:
        i, a = int_of(v), abs_of(v)
        if all(not isinstance(w, Num) or not (float(w) == math.trunc(float(w)) and 1e15 <= abs(float(w)) < TWO_53) for w in (i, a)):
            lines.append(f'say int({lit(v)}), " ", abs({lit(v)});')
            out.append(f'{show(i)} {show(a)}')
    # Through strings, booleans and as named unary operators (D41).
    lines += [
        'say int("3.7"), " ", int(" -12 "), " ", int("1e3"), " ", int("1.5e2"), " ", int("0.99999999999999995"), " ", abs("-0.99999999999999995");',
        'say abs("-3.0"), " ", abs("-12.0"), " ", abs("-9007199254740992.0"), " ", int("-1e15");',
        'say int(true), abs(false), " ", int 7 / 2, " ", abs -3, " ", int(7.5) + 1, " ", abs(-2) ** 3;',
        'my @a = (1, 2, 3); say int(@a), " ", abs(@a);',
        'my $x = -2.5; say int($x) . "|" . abs($x);',
    ]
    out += ['3 -12 1000 150 1 1', '3 12 9.00719925474099e+15 -1000000000000000', '10 3 3 8 8', '3 3', '-2|2.5']
    return lines, out


def case_float(rnd):
    lines, out = [], []
    args = [0, 1, 2, -1, 10, 100, Num(0.5), Num(-0.5), Num(1e-10), Num(3.14159), Num(-2.5), Num(700.0), Num(-700.0), Num(1e10), 12345]
    for _ in range(30):
        args.append(Num(rnd.uniform(-50, 50)))
    for v in args:
        x = float(v)
        row = [Num(math.sin(x)), Num(math.cos(x))]
        names = ['sin', 'cos']
        if x < 709:
            row.append(Num(math.exp(x)))
            names.append('exp')
        if x >= 0:
            row.append(Num(math.sqrt(x)))
            names.append('sqrt')
        if x > 0:
            row.append(Num(math.log(x)))
            names.append('log')
        lines.append('say ' + ', " ", '.join(f'{n}({lit(v)})' for n in names) + ';')
        out.append(' '.join(show(w) for w in row))
    for _ in range(30):
        y = Num(rnd.uniform(-10, 10)) if rnd.random() < 0.7 else rnd.randint(-5, 5)
        x = Num(rnd.uniform(-10, 10)) if rnd.random() < 0.7 else rnd.randint(-5, 5)
        lines.append(f'say atan2({lit(y)}, {lit(x)});')
        out.append(show(Num(math.atan2(float(y), float(x)))))
    lines += [
        'say atan2(1, 1) * 4, " ", atan2(0, 0), " ", atan2(0, 1), " ", atan2(1, 0), " ", atan2(0, -1);',
        'say sqrt 4 * 9, " ", sqrt(16), " ", exp(0), " ", log(1), " ", cos(0), " ", sin(0);',
        'say sqrt("2.25"), " ", exp(" 1 "), " ", log("1e2"), " ", sqrt(true), " ", sin(false);',
        'my $z = 0.0; say sqrt(-$z), " ", sin(-$z), " ", cos(-$z), " ", exp(-$z);',
        'say exp(-700), " ", sqrt(9007199254740993), " ", log(9223372036854775807);',
        'my @a = (1, 2, 3, 4); say sqrt(@a), " ", log(@a);',
    ]
    out += [show(Num(math.atan2(1, 1) * 4)) + ' 0 0 ' + show(Num(math.atan2(1, 0))) + ' ' + show(Num(math.atan2(0, -1))),
            '6 4 1 0 1 0', f'1.5 {show(Num(math.exp(1)))} {show(Num(math.log(100)))} 1 0', '0 0 1 1',
            f'{show(Num(math.exp(-700)))} {show(Num(math.sqrt(float(9007199254740993))))} {show(Num(math.log(float(9223372036854775807))))}',
            f'2 {show(Num(math.log(4)))}']
    return lines, out


def based(s, base):
    v = 0
    us = False
    if s.startswith('_'):
        s = s[1:]
        us = True
        assert s
    for i, ch in enumerate(s):
        if ch == '_':
            assert not us and i != len(s) - 1
            us = True
            continue
        us = False
        v = v * base + int(ch, 16)
    return v


def digits_of(rnd, base, n):
    alphabet = '0123456789abcdefABCDEF'[:base if base <= 10 else 22] if base != 16 else '0123456789abcdefABCDEF'
    out = '_' if rnd.random() < 0.15 else ''
    for k in range(n):
        out += rnd.choice(alphabet)
        if k < n - 1 and rnd.random() < 0.15:
            out += '_'
    return out


def case_hex_oct(rnd):
    lines, out = [], []
    for _ in range(40):
        d = digits_of(rnd, 16, rnd.randint(0, 8))
        pre = rnd.choice(['', '', '0x', '0X', 'x', 'X'])
        s = pre + d
        if d == '_':
            continue
        v = based(d, 16) if d else 0
        if v > 0xFFFFFFFF:
            continue
        lines.append(f'say hex("{s}");')
        out.append(str(v))
    for _ in range(60):
        base = rnd.choice([2, 8, 8, 16])
        pre = {2: rnd.choice(['0b', '0B', 'b', 'B']), 8: rnd.choice(['', '', '0', '0o', 'o', 'O', '0O']), 16: rnd.choice(['0x', 'x', '0X', 'X'])}[base]
        d = digits_of(rnd, base, rnd.randint(0, 11 if base == 8 else 33 if base == 2 else 8))
        if d == '_':
            continue
        lead = rnd.choice(['', '', ' ', '  ', '\\t', '\\n '])
        v = based(d, base) if d else 0
        if v > 0xFFFFFFFF:
            continue
        lines.append(f'say oct("{lead}{pre}{d}");')
        out.append(str(v))
    lines += [
        'say hex("ffffffff"), " ", oct("37777777777"), " ", oct("0b" . "1" x 32), " ", hex(""), " ", oct(""), " ", hex("0x"), " ", oct("0b");',
        'say hex(255), " ", oct(10), " ", hex(1.5 * 2), " ", oct(true), " ", hex(false), " ", hex "a" . "b";',
        'my $s = "0x1F"; say oct($s), " ", hex($s), " ", oct(lc $s);',
    ]
    out += ['4294967295 4294967295 4294967295 0 0 0 0', f'{0x255} 8 3 1 0 171', '31 31 31']
    return lines, out


def bits(v):
    if isinstance(v, Num):
        v = int(math.trunc(float(v)))
    return v & (TWO_64 - 1)


def operand(rnd):
    r = rnd.random()
    if r < 0.4:
        return rnd.randint(-1000, 1000)
    if r < 0.6:
        return rnd.randint(-TWO_63 + 1, TWO_63 - 1)
    if r < 0.8:
        return Num(rnd.uniform(-1e6, 1e6))
    return rnd.choice([0, -1, 1, 255, TWO_63 - 1, -TWO_63 + 1, Num(0.999), Num(-0.999), Num(-1.5)])


def case_bits(rnd):
    lines, out = [], []
    n = 0
    while n < 150:
        a, b = operand(rnd), operand(rnd)
        op = rnd.choice(['&', '|', '^', '~'])
        if op == '~':
            r = ~bits(a) & (TWO_64 - 1)
            text = f'~{lit(a)}'
        else:
            r = {'&': bits(a) & bits(b), '|': bits(a) | bits(b), '^': bits(a) ^ bits(b)}[op]
            text = f'{lit(a)} {op} {lit(b)}'
        if r >= TWO_63:
            continue
        lines.append(f'say({text});')
        out.append(str(r))
        n += 1
    lines += [
        'say "12" & "10", " ", "12" | 3, " ", " 6 " ^ "3", " ", true & 3, " ", false | 0, " ", ~-1, " ", ~(-6);',
        'say 6 & (3 == 3), " ", 6 | (3 < 3), " ", 6 ^ 3 eq 3, " ", (6 & 3) == 2;',
        'say 1 | 2 & 3, " ", 1 ^ 3 | 4, " ", 12 & 10 ^ 6, " ", -1 & 255 | 256;',
        'my @a = (1, 2, 3); say @a & 1, " ", @a | 4;',
        'say "1.5" & 3, " ", 3.99 | 0, " ", -3.99 & 255, " ", "1e3" & 1023;',
        'my $x = 12; say $x &3, " ", $x |1, " ", $x ^1;',
    ]
    out += ['8 15 5 1 0 0 5', '0 6 7 1', '3 6 14 511', '1 7', '1 3 253 1000', '0 13 13']
    return lines, out


def shl(a, c):
    u = bits(a)
    if c < 0:
        return shr(a, -c)
    return 0 if c >= 64 else (u << c) & (TWO_64 - 1)


def shr(a, c):
    u = bits(a)
    if c < 0:
        return shl(a, -c)
    return 0 if c >= 64 else u >> c


def case_shifts(rnd):
    lines, out = [], []
    n = 0
    while n < 150:
        a = operand(rnd)
        c = rnd.choice([rnd.randint(-70, 70), rnd.randint(0, 64), rnd.randint(-TWO_63 + 1, TWO_63 - 1)])
        op = rnd.choice(['<<', '>>'])
        r = shl(a, c) if op == '<<' else shr(a, c)
        if r >= TWO_63:
            continue
        lines.append(f'say({lit(a)} {op} {lit(c)});')
        out.append(str(r))
        n += 1
    lines += [
        'say 1 << 62, " ", 5 << 62, " ", -1 >> 1, " ", -8 >> 1, " ", 1 << 64, " ", 1 << -1, " ", 8 >> -1, " ", 1 >> 64;',
        'say 1 << 1.9, " ", 1 << "3", " ", 2 ** 3 << 1, " ", 1 + 1 << 2, " ", 1 << 2 + 1, " ", length("ab") << 2;',
        'my $x = 6; $x &= 3; my $y = 6; $y |= 8; my $z = 6; $z ^= 5; my $l = 3; $l <<= 4; my $r = 100; $r >>= 2; say "$x $y $z $l $r";',
        'my $u; $u |= 5; my $v; $v ^= 3; say "$u $v";',
        'my @a = (1, 2); $a[0] |= 4; $a[1] <<= 3; my %h = (k => 7); $h{k} &= 3; $h{n} ^= 9; say "@a $h{k} $h{n}";',
        'my $s = "12"; $s &= "10"; say $s;',
        'say 1 << (-9223372036854775807 - 1), " ", 8 >> (-9223372036854775807 - 1), " ", 3 >> -2, " ", 3 << -2;',
    ]
    out += ['4611686018427387904 4611686018427387904 9223372036854775807 9223372036854775804 0 0 16 0', '2 8 16 8 8 8',
            '2 14 3 48 25', '5 3', '5 16 3 9', '8', '0 0 12 0']
    return lines, out


class Rand:
    def __init__(self):
        self.x = 0

    def srand(self, s):
        self.x = 0x330E + ((s & 0xFFFFFFFF) << 16)

    def next(self):
        self.x = (self.x * 0x5DEECE66D + 0xB) & 0xFFFFFFFFFFFF
        return self.x / 2 ** 48


def case_rand(rnd):
    g = Rand()
    lines, out = [], []
    for seed in [0, 1, 42, 4294967295, 4294967296 + 42, 123456789, 1000]:
        lines.append(f'srand({seed});')
        g.srand(seed)
        for _ in range(6):
            k = rnd.choice(['none', 'int', 'num', 'zero', 'neg'])
            if k == 'none':
                lines.append('say rand();')
                out.append(show(Num(g.next())))
            elif k == 'int':
                n = rnd.randint(1, 1000)
                lines.append(f'say int(rand({n}));')
                out.append(str(int(math.trunc(n * g.next()))))
            elif k == 'num':
                n = Num(rnd.uniform(0.1, 1e6))
                lines.append(f'say rand({lit(n)});')
                out.append(show(Num(float(n) * g.next())))
            elif k == 'zero':
                lines.append('say rand(0);')
                out.append(show(Num(g.next())))
            else:
                n = -rnd.randint(1, 100)
                lines.append(f'say rand({n});')
                out.append(show(Num(n * g.next())))
    lines += ['say srand(42), " ", srand(0), " ", srand(4294967296), " ", srand("7"), " ", srand("042"), " ", srand(42.0);']
    out += ['42 0 but true 4294967296 7 42 42']
    g.srand(42)
    lines += ['srand(3); my @a = map { int rand 6 } 1 .. 10; say "@a";', 'srand 9; my @b = (5, 6, 7); say $b[rand @b], " ", int(rand(@b)), " ", int rand 10;',
              'srand(1); rand; rand(10); say rand;']
    g.srand(3)
    out.append(' '.join(str(int(6 * g.next())) for _ in range(10)))
    g.srand(9)
    b = [5, 6, 7]
    out.append(f'{b[int(3 * g.next())]} {int(3 * g.next())} {int(10 * g.next())}')
    g.srand(1)
    g.next()
    g.next()
    out.append(show(Num(g.next())))
    return lines, out


CASES = {4400: case_int_abs, 4401: case_float, 4402: case_hex_oct, 4500: case_bits, 4501: case_shifts, 4600: case_rand}


def main(argv):
    program = argv[0] == '--program'
    n = int(argv[-1])
    lines, out = CASES[n](random.Random(n))
    if program:
        sys.stdout.write(f'# t/models/numfn.py {n}\nuse v5.42;\n' + '\n'.join(lines) + '\n')
    else:
        sys.stdout.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])
