#!/usr/bin/env python3
# Writes step 22's fault and refusal tests from tables written by hand, as
# docs/briefs/step16c-tests.py does. Nothing here asks the compiler. What
# perl does with each is in its comment, pasted from perl 5.42
# (briefs/claims22.py has the programs).
#
#     python3 docs/briefs/step22-tests.py
import sys

GROUPS = {'a': [], 'b': [], 'c': []}
R = []


def f(group, name, why, body, before, message, line):
    GROUPS[group].append((name, why, body, before, message, line))


def r(name, why, body, at, message, nth=1):
    R.append((name, why, body, at, message, nth))


WHOLE_FLOAT = 'a whole float this size prints two ways in perl (add 0 to print the integer)'
SPLIT = 'a string with a point this close to the next whole number has two values in perl'
OUTSIDE = 'a number outside the integers where a whole number is wanted'
UNSIGNED = "a bitwise answer of 2^63 or more: perl's is an unsigned integer, which the language does not have"
HEX = 'hex of a string that is not all digits of its base: perl warns, or stops there in silence'
OCT = 'oct of a string that is not all digits of its base: perl warns, or stops there in silence'
SRAND = 'srand of a negative number, a fraction, a boolean or a string that is not digits alone: perl reads its argument as a string of digits'
MINUS_ZERO = lambda fn: f'a string that is a zero with a minus, to {fn}: perl reads it as -0 or 0 by what the string was used as'
UNDERFLOW = 'an uncaught die after a number underflowed: perl exits with the status of $! there, which the language does not keep'

# ---- 22a: the numeric builtins
f('a', 'int-past-2-63', 'perl gives the unsigned integer 9300000000000000000 (T470).', 'say int(9.2e18);\nsay int(9.3e18);', '9200000000000000000\n', 'int of a number from 2^63 to 2^64: perl gives an unsigned integer, which the language does not have', 2)
f('a', 'abs-of-the-smallest', 'perl gives the unsigned integer 9223372036854775808 (T471).', 'my $x = -9223372036854775807;\nsay abs($x);\n$x = $x - 1;\nsay abs($x);', '9223372036854775807\n', 'abs of -2^63: perl gives the unsigned integer 2^63, which the language does not have', 4)
f('a', 'abs-of-a-point-string', 'perl takes a string with a point for a float, and prints 1e+15 (T487); the Num is D36\'s.', 'say abs("-12.0");\nsay abs("-1000000000000000.0");', '12\n', WHOLE_FLOAT, 2)
f('a', 'sqrt-below-zero', "perl dies: Can't take sqrt of -1e-300 (T481).", 'say sqrt(0);\nsay sqrt(-1e-300);', '0\n', 'sqrt of a number below zero', 2)
f('a', 'log-of-zero', "perl dies: Can't take log of 0 (T481).", 'say log(1);\nsay log(0);', '0\n', 'log of zero or a number below zero', 2)
f('a', 'log-of-a-negative-zero', "perl dies: Can't take log of -0 (T481).", 'my $z = 0.0;\nsay log(-$z);', '', 'log of zero or a number below zero', 2)
f('a', 'log-below-zero', "perl dies: Can't take log of -1.", 'say log(-1);', '', 'log of zero or a number below zero', 1)
f('a', 'exp-overflow', 'perl prints Inf (D37).', 'say exp(709);\nsay exp(710);', '8.21840746155497e+307\n', 'float overflow', 2)
f('a', 'atan2-negative-zero-x', 'perl prints pi, or 0 once the zero has been used as an integer (T79, T484).', 'my $z = 0.0;\nsay atan2(0, $z);\nsay atan2(0, -$z);', '0\n', "a negative zero to atan2: perl's answer turns on whether the zero was used as an integer", 3)
f('a', 'atan2-negative-zero-y', 'perl prints -pi, or pi once the zero has been used as an integer (T484).', 'my $z = 0.0;\nsay atan2(-$z, -1);', '', "a negative zero to atan2: perl's answer turns on whether the zero was used as an integer", 2)
f('a', 'atan2-minus-zero-string', 'perl prints pi, or 0 once the string has been added to (T484).', 'say atan2(0, "0");\nsay atan2(0, "-0");', '0\n', MINUS_ZERO('atan2'), 2)
f('a', 'sin-minus-zero-string', 'perl gives -0 or 0, which atan2 tells apart (T484).', 'say sin("0");\nsay sin("-0");', '0\n', MINUS_ZERO('sin'), 2)
f('a', 'sqrt-minus-zero-string', 'perl gives -0 or 0.', 'say sqrt(" -0.0");', '', MINUS_ZERO('sqrt'), 1)
f('a', 'exp-minus-zero-string', 'perl gives 1 either way; the rule is one for the six (D202).', 'say exp("-0");', '', MINUS_ZERO('exp'), 1)
f('a', 'underflow-then-die', 'perl exits 34, the ERANGE exp set (T472, D151).', 'my $v = -745.2;\nmy $x = exp($v);\nsay "after";\ndie "x\\n";', 'after\n', UNDERFLOW, 4)
f('a', 'subnormal-then-die', 'perl exits 255 here, the C library not setting errno for atan2 (T472): the language marks every underflow.', 'my $v = 1e-300;\nmy $x = atan2($v, 1e10);\ndie "x\\n";', '', UNDERFLOW, 3)
f('a', 'atan2-of-minus-abs-of-a-point-string', 'perl\'s abs("0.0") is a float, so its negation is -0, and atan2 prints pi (the review\'s finding 2).', 'say atan2(0, -abs("0"));\nsay atan2(0, -abs("0.0"));', '0\n', "a negative zero to atan2: perl's answer turns on whether the zero was used as an integer", 2)
f('a', 'int-of-undef', 'perl warns: Use of uninitialized value in int.', 'my $u;\nsay int($u);', '', 'undef where a number is wanted', 2)
f('a', 'sqrt-of-undef', 'perl warns: Use of uninitialized value in sqrt.', 'my $u;\nsay sqrt($u);', '', 'undef where a number is wanted', 2)
f('a', 'int-of-a-reference', 'perl prints the address (D112).', 'my $r = [1];\nsay int($r);', '', 'a reference where a number is wanted', 2)
f('a', 'cos-of-a-reference', 'perl takes the address (D112).', 'my $r = {};\nsay cos($r);', '', 'a reference where a number is wanted', 2)
f('a', 'hex-of-a-reference', "perl warns: Illegal hexadecimal digit 'R' ignored, and prints 10 (D112).", 'my $r = [1];\nsay hex($r);', '', 'a reference where a string is wanted', 2)
f('a', 'int-not-numeric', 'perl warns: Argument "abc" isn\'t numeric in int.', 'say int("abc");', '', 'not a numeric string', 1)
f('a', 'hex-of-undef', 'perl warns: Use of uninitialized value in hex.', 'my $u;\nsay hex($u);', '', 'undef where a string is wanted', 2)
f('a', 'hex-illegal-digit', "perl warns: Illegal hexadecimal digit 'g' ignored (T473).", 'say hex("ff");\nsay hex("fg");', '255\n', HEX, 2)
f('a', 'hex-blank-first', "perl warns: Illegal hexadecimal digit ' ' ignored, and gives 0 (T473).", 'say hex(" ff");', '', HEX, 1)
f('a', 'hex-underscore-last', "perl warns: Illegal hexadecimal digit '_' ignored (T473).", 'say hex("_ff");\nsay hex("ff_");', '255\n', HEX, 2)
f('a', 'hex-two-underscores', "perl warns: Illegal hexadecimal digit '_' ignored, and gives 15 (T473).", 'say hex("f_f");\nsay hex("f__f");', '255\n', HEX, 2)
f('a', 'hex-past-32-bits', 'perl warns: Hexadecimal number > 0xffffffff non-portable (T473).', 'say hex("ffffffff");\nsay hex("100000000");', '4294967295\n', 'hex of a number past 32 bits: perl warns that it is not portable', 2)
f('a', 'hex-of-a-whole-float', 'perl makes the string 1e+15, and stops at the plus (D36).', 'say hex(1e15);', '', WHOLE_FLOAT, 1)
f('a', 'oct-past-32-bits', 'perl warns: Octal number > 037777777777 non-portable (T473).', 'say oct("37777777777");\nsay oct("40000000000");', '4294967295\n', 'oct of a number past 32 bits: perl warns that it is not portable', 2)
f('a', 'oct-binary-past-32-bits', 'perl warns: Binary number > 0b11111111111111111111111111111111 non-portable.', 'say oct("0b" . "1" x 33);', '', 'oct of a number past 32 bits: perl warns that it is not portable', 1)
f('a', 'oct-blank-last', 'perl gives 493 in silence (T473): a stop it makes in silence is a fault here (D203).', 'say oct(" 755");\nsay oct("755 ");', '493\n', OCT, 2)
f('a', 'oct-letter', 'perl gives 7 in silence (T473).', 'say oct("7z");', '', OCT, 1)
f('a', 'oct-minus', 'perl gives 0 in silence (T473).', 'say oct("-10");', '', OCT, 1)
f('a', 'oct-eight', "perl warns: Illegal octal digit '8' ignored, and gives 7 (T473).", 'say oct("789");', '', OCT, 1)
f('a', 'oct-binary-two', "perl warns: Illegal binary digit '2' ignored, and gives 2 (T473).", 'say oct("0b101");\nsay oct("0b102");', '5\n', OCT, 2)
f('a', 'oct-hex-letter', "perl warns: Illegal hexadecimal digit 'g' ignored, and gives 1.", 'say oct("0x1g");', '', OCT, 1)

# ---- 22b: the bit operators
f('b', 'complement-of-zero', 'perl prints 18446744073709551615 (T474).', 'say ~-1;\nsay ~0;', '0\n', UNSIGNED, 2)
f('b', 'or-of-minus-one', 'perl prints 18446744073709551615 (T474).', 'say -1 & 1;\nsay -1 | 0;', '1\n', UNSIGNED, 2)
f('b', 'xor-to-the-top', 'perl prints 18446744073709551615.', 'say 1 ^ -2;', '', UNSIGNED, 1)
f('b', 'shift-to-2-63', 'perl prints 9223372036854775808 (T474).', 'say 1 << 62;\nsay 1 << 63;', '4611686018427387904\n', UNSIGNED, 2)
f('b', 'shift-left-by-a-negative', 'perl shifts the other way: 9223372036854775808.', 'say 1 >> -63;', '', UNSIGNED, 1)
f('b', 'shift-a-negative', 'perl prints 18446744073709551614.', 'say -1 >> 0;', '', UNSIGNED, 1)
f('b', 'operand-past-the-ints', 'perl takes 1e19 as the unsigned integer, and prints 0.', 'say 1e19 & 1;', '', OUTSIDE, 1)
f('b', 'count-past-the-ints', 'perl clamps the count, and prints 0.', 'say 1 << 1e19;', '', OUTSIDE, 1)
f('b', 'operand-split', 'perl prints 0, or 1 once the string has been used as a float (T475).', 'say "0.99999999999999995" | 0;', '', SPLIT, 1)
f('b', 'count-split', 'perl shifts by 0 or 1 by the string\'s past (T475).', 'say 1 << "0.99999999999999995";', '', SPLIT, 1)
f('b', 'and-assign-undef', 'perl warns: Use of uninitialized value $x in numeric bitwise and (T477).', 'my $x;\n$x &= 5;', '', 'undef where a number is wanted', 2)
f('b', 'shift-assign-undef', 'perl warns: Use of uninitialized value $x in left bitshift (T477).', 'my $x;\n$x <<= 1;', '', 'undef where a number is wanted', 2)
f('b', 'right-shift-assign-undef', 'perl warns: Use of uninitialized value $x in right bitshift (T477).', 'my $x;\n$x >>= 1;', '', 'undef where a number is wanted', 2)
f('b', 'or-of-undef', 'perl warns: Use of uninitialized value $u in numeric bitwise or.', 'my $u;\nsay $u | 1;', '', 'undef where a number is wanted', 2)
f('b', 'or-assign-undef-on-the-right', 'perl warns: Use of uninitialized value $u in numeric bitwise or.', 'my $x = 1;\nmy $u;\n$x |= $u;', '', 'undef where a number is wanted', 3)
f('b', 'or-of-a-reference', 'perl takes the address (D112).', 'my $r = [];\nsay $r | 0;', '', 'a reference where a number is wanted', 2)
f('b', 'complement-of-a-reference', 'perl takes the address (D112).', 'my $r = [];\nsay ~$r;', '', 'a reference where a number is wanted', 2)
f('b', 'and-not-numeric', 'perl warns: Argument "abc" isn\'t numeric in numeric bitwise and.', 'say "abc" & 1;', '', 'not a numeric string', 1)
f('b', 'shift-count-not-numeric', 'perl warns: Argument "A" isn\'t numeric in left bitshift.', 'my $y = 6 << "A";', '', 'not a numeric string', 1)

# ---- 22c: rand, srand and time
f('c', 'srand-negative', 'perl seeds as srand(1), and gives 1 (T479).', 'srand(-1);', '', SRAND, 1)
f('c', 'srand-fraction', 'perl seeds as srand(1) (T479).', 'srand(1.9);', '', SRAND, 1)
f('c', 'srand-small-float', 'perl warns: Integer overflow in srand (T479).', 'srand(1e-5);', '', SRAND, 1)
f('c', 'srand-big-float', 'perl warns: Integer overflow in srand, the string being 1e+15.', 'srand(999999999999999);\nsrand(1e15);', '', SRAND, 2)
f('c', 'srand-exponent-string', 'perl warns: Integer overflow in srand (T479).', 'srand("1e3");', '', SRAND, 1)
f('c', 'srand-blanks', 'perl seeds as 42 (T479); only digits alone are taken here.', 'srand("42");\nsrand(" 42 ");', '', SRAND, 2)
f('c', 'srand-plus', 'perl seeds as 5 (T479).', 'srand("+5");', '', SRAND, 1)
f('c', 'srand-empty', 'perl warns: Integer overflow in srand.', 'srand("");', '', SRAND, 1)
f('c', 'srand-true', 'perl seeds as 1 (T479).', 'srand(true);', '', SRAND, 1)
f('c', 'srand-false', 'perl warns: Integer overflow in srand (T479).', 'srand(false);', '', SRAND, 1)
f('c', 'srand-undef', 'perl warns: Use of uninitialized value in srand, and Integer overflow.', 'my $u;\nsrand($u);', '', 'undef where a number is wanted', 2)
f('c', 'srand-reference', 'perl reads the string ARRAY(0x...), and warns: Integer overflow in srand.', 'my $r = [];\nsrand($r);', '', 'a reference where a number is wanted', 2)
f('c', 'srand-digits-past-the-ints', 'perl warns: Integer overflow in srand.', 'srand("9223372036854775807");\nsrand("9223372036854775808");', '', 'integer overflow', 2)
f('c', 'rand-of-undef', 'perl warns: Use of uninitialized value in rand.', 'srand(1);\nmy $u;\nsay rand($u);', '', 'undef where a number is wanted', 3)
f('c', 'rand-not-numeric', 'perl warns: Argument "abc" isn\'t numeric in rand.', 'say rand("abc");', '', 'not a numeric string', 1)
f('c', 'rand-of-a-reference', 'perl takes the address (D112).', 'my $r = [];\nsay rand($r);', '', 'a reference where a number is wanted', 2)

# ---- refusals
AMBIGUOUS = lambda w, s: f'{w} {s}: perl warns that this is ambiguous: write {w}({s}...)'
ARG = lambda w, op: f"{w} before '{op}': perl takes what follows {w} for its argument; write {w}() {op} ..."
D53 = "'=' where a value is tested, with nothing but a constant on its right: perl warns that == was meant"
USELESS = 'this statement only has a value, and nothing is done with it: perl warns that it is useless'
HANDLE = lambda s, rest: f"say $x {s}{rest}: perl takes $x for a file handle here; put a blank after the '{s}', or none before it"
PREC = lambda c, b: f"'{c}' as an operand of '{b}': perl warns of a precedence problem, '{b}' binding more loosely; bracket the one that is meant"
CUT = lambda op: f"'{op}' is perl's string bitwise operator, which is cut (D204): the bit operators here are numeric"
r('int-no-argument', 'perl takes $_.', 'say int;', 'int', 'int needs an argument')
r('hex-no-argument', 'perl takes $_.', 'say hex();', 'hex', 'hex needs an argument')
r('abs-minus', 'perl warns: Use of "abs" without parentheses is ambiguous (T485).', 'say abs - 5;', '-', AMBIGUOUS('abs', '-'))
r('sqrt-plus', 'perl warns: Use of "sqrt" without parentheses is ambiguous.', 'say sqrt + 4;', '+', AMBIGUOUS('sqrt', '+'))
r('rand-plus', 'perl warns: Use of "rand" without parentheses is ambiguous (T485).', 'my $x = rand + 1;', '+', AMBIGUOUS('rand', '+'))
r('rand-star', 'perl takes *2 for a glob, rand\'s argument (T485).', 'my $x = rand * 2;', 'rand', ARG('rand', '*'))
r('rand-less-than', 'perl reads <0.5 ... as a glob.', 'say "y" if rand < 0.5;', 'rand', ARG('rand', '<'))
r('rand-slash', 'perl reads / 2;... as a pattern.', 'my $x = rand / 2;', 'rand', ARG('rand', '/'))
r('srand-star', 'perl takes *2 for a glob, srand\'s argument.', 'my $x = srand * 2;', 'srand', ARG('srand', '*'))
r('rand-two-arguments', 'perl does not compile it: Too many arguments for rand.', 'say rand(1, 2);', ',', "expected ')', found ','")
r('atan2-no-brackets', 'perl takes it: 0.785398163397448.', 'say atan2 1, 1;', 'atan2', 'atan2 needs brackets round its arguments: atan2(...)')
r('atan2-one-argument', 'perl does not compile it: Not enough arguments for atan2.', 'say atan2(1);', 'atan2', 'atan2 takes 2 to 2 arguments, and here are 1')
r('time-argument', 'perl does not compile it: syntax error.', 'say time(1);', '1)', 'time takes no argument')
r('time-alone', 'perl warns: Useless use of time in void context (T483).', 'time;', 'time', USELESS)
r('int-alone', 'perl warns: Useless use of a constant (3) in void context (T483).', 'int(3);', 'int', USELESS)
r('tested-int', 'perl folds int(3.5) and warns: Found = in conditional (T482).', 'my $x;\nif ($x = int(3.5)) { say $x }', '=', D53)
r('tested-bits', 'perl folds 1 | 2 and warns: Found = in conditional (T482).', 'my $x;\nif ($x = 1 | 2) { say $x }', '=', D53)
r('tested-hex', 'perl folds hex("ff") and warns: Found = in conditional (T482).', 'my $x;\nwhile ($x = hex("ff")) { last }', '=', D53)
r('tested-shift', 'perl folds 1 << 2 and warns.', 'my $x;\nsay "y" unless $x = 1 << 2;', '=', D53)
r('tilde-after-say-variable', 'perl takes $x for a file handle and dies (T478).', 'my $x = -6;\nsay $x ~5;', '$x ~', HANDLE('~', '5'))
r('tilde-blank-after-say-variable', 'perl takes $x for a file handle and dies (T478).', 'my $x = -6;\nsay $x ~ 5;', '$x ~', HANDLE('~', ' '))
r('heredoc-after-say-variable', 'perl looks for a heredoc ended by 1, and does not compile (T478).', 'my $x = 6;\nsay $x <<1;', '$x <<', HANDLE('<<', '1'))
r('heredoc-after-print-variable', 'perl does not compile: Use of bare << to mean <<"" is forbidden (T478).', 'my $x = 6;\nprint $x <<(1);', '$x <<', "print $x <<(: perl takes $x for a file handle here; put a blank after the '<<', or none before it")
r('string-and', 'perl prints 10: the string bitwise and (T46).', 'say "12" &. "10";', '&.', CUT('&.'))
r('string-complement', 'perl gives the string with each character complemented.', 'say ~."a";', '~.', CUT('~.'))
r('string-or-assign', 'perl or-s the strings.', 'my $s = "a";\n$s |.= " ";', '|.=', CUT('|.='))
r('string-and-hard-against', 'perl takes &. for the string operator: 6 &.5 is "6" &. "5", 4 (the review\'s finding 6).', 'say 6 &.5;', '&.', CUT('&.'))
r('string-complement-hard-against', 'perl takes ~. for the string operator: ~."5".', 'say ~.5;', '~.', CUT('~.'))
r('comparison-under-and', 'perl warns: Possible precedence problem on bitwise & operator (T489).', 'my $y = 3;\nsay 6 & $y == 3;', '==', PREC('==', '&'))
r('comparison-over-or', 'perl warns: Possible precedence problem on bitwise | operator (T489).', 'my $y = 3;\nsay $y < 3 | 6;', '<', PREC('<', '|'))
r('spaceship-under-xor', 'perl warns: Possible precedence problem on bitwise ^ operator (T489).', 'my $z = 6;\nsay $z ^ $z <=> 1;', '<=>', PREC('<=>', '^'))
r('constant-comparison-under-and', 'perl folds 3 == 3 and is silent (T486): refused all the same (D208).', 'say 6 & 3 == 3;', '==', PREC('==', '&'))
r('handle-after-atan2', 'perl does not compile it: Missing comma after first argument to atan2 function.', 'my $x = 3;\nsay atan2($x -1, 1);', '$x -', "atan2 $x -1: perl takes $x for a file handle here; put a blank after the '-', or none before it")
r('heredoc-after-atan2', 'perl looks for a heredoc ended by 1.', 'my $x = 3;\nsay atan2($x <<1, 1);', '$x <<', "atan2 $x <<1: perl takes $x for a file handle here; put a blank after the '<<', or none before it")
r('smartmatch-tilde', 'perl prints 5: two complements, in prefix.', 'say ~~5;', '~~', "'~~' is not in the language yet")
r('use-integer', 'perl makes the bit operators signed, and every arithmetic operator an integer one.', 'use integer;\nsay ~0;', 'integer', "'use integer' is not in the language")
r('localtime', 'perl gives the date as a string: step 22d (D200).', 'my $s = localtime;', 'localtime', "expected a value, found 'localtime'")
r('sleep', 'perl sleeps a second: step 22d (D200).', 'sleep(1);', 'sleep', "'sleep' is not in the language")


def write():
    starts = {'a': 4440, 'b': 4540, 'c': 4640}
    for group, first in starts.items():
        n = first
        for name, why, body, before, message, line in GROUPS[group]:
            program = f'# kind: fault\n# {why}\nuse v5.42;\n{body}\n'
            path = f't/{n}-fault-{name}'
            open(path + '.pl', 'w', encoding='utf-8').write(program)
            open(path + '.expected', 'w', encoding='utf-8').write(f'{before}fault: {message} at {path}.pl line {line + 3}.\nexit: 1\n')
            n += 1
        print(n - first, 'fault tests,', first, 'to', n - 1)
    first = 4660
    n = first
    for name, why, body, at, message, nth in R:
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-{name}'
        open(path + '.pl', 'w', encoding='utf-8').write(program)
        k = program.index('use v5.42;')
        for _ in range(nth):
            k = program.index(at, k + 1)
        line = program.count('\n', 0, k) + 1
        col = len(program[program.rfind('\n', 0, k) + 1:k]) + 1
        open(path + '.expected', 'w', encoding='utf-8').write(f'{path}.pl:{line}:{col}: {message}\nexit: 1\n')
        n += 1
    print(n - first, 'refusal tests,', first, 'to', n - 1)


if __name__ == '__main__':
    write()
