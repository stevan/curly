#!/usr/bin/env python3
# Writes the refusal tests of step 19's independent review (T560 to T570)
# from a table written by hand, as docs/briefs/step19-refusals.py writes the
# step's own: the program, the text the message points at (its column is
# counted here, from the program's own text), and the message. Nothing here
# asks the compiler. What perl does with each is in its comment, from perl
# 5.42 run plain (`--perl` prints each again).
#
#     python3 docs/briefs/step19-review/review-refusals.py 5469
import os
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

S = 'my $s = "ab";\n'
TWICE = "'{0}' twice in a class: perl may take it for a POSIX class without its brackets, and warn (T565); write \\{0}"
LETTERS = "'{0}' and letters in a row in a class: perl may take it for a POSIX class without its brackets, and warn (T565); write \\{0}"
HEX = '\\x and one hex digit: perl warns unless the pattern ends there (T562); write two, \\x04, or \\x{...}'
ZERO = 'a count with a leading zero in a quantifier: perl does not compile it (Invalid quantifier, T564)'
EMPTY = 'a class that matches no character: perl warns of a quantifier on it (T566)'
NAMED = "\\N{U+...} before a blank or '#' in a class under /x: perl skips the blank there, as it does nowhere else in a class (T567); write \\x{...}"

# ---- what stands round the pattern
r('not-match-on-the-left', "perl warns: Possible precedence problem between ! and pattern match (m//), and prints an empty line (T560).", S + 'say $s !~ /a/ =~ /1/;', '=~',
  "a '!~' match on the left of '=~': perl warns of a precedence problem between ! and the match (T547, T560); bracket it, (... !~ ...) =~ ...")
r('not-match-on-the-left-of-not', "perl warns the same, and prints 1.", S + 'say $s !~ /a/ !~ /1/;', '!~',
  "a '!~' match on the left of '!~': perl warns of a precedence problem between ! and the match (T547, T560); bracket it, (... !~ ...) !~ ...", nth=2)
r('power-after', "perl prints 1: $_ is matched, the answer raised, and that number is the pattern (T561). The compiler printed 0.", 'for ("a") {\n    say "1" =~ /a/ ** 2;\n}', '**',
  "'**' after the pattern of '=~': it binds tighter, so perl matches the pattern against $_ and raises that (T561); bracket the match, (... =~ /.../) ** ...")
r('power-after-not', "perl prints 1 (T561). The compiler printed 0.", S + 'for ("a") {\n    say $s !~ m{a} ** 2;\n}', '**',
  "'**' after the pattern of '!~': it binds tighter, so perl matches the pattern against $_ and raises that (T561); bracket the match, (... !~ /.../) ** ...")
# ---- in the pattern
r('one-hex-digit', "perl warns: Non-hex character '-' terminates \\x early. Resolved as \"\\x04-\" (T562).", S + 'say $s =~ /\\x4-/ ? 1 : 0;', '\\x4', HEX)
r('one-hex-digit-in-a-class', "perl warns: Non-hex character ']' terminates \\x early (T562).", S + 'say $s =~ /[\\x4]/ ? 1 : 0;', '\\x4', HEX)
r('dollar-before-comment', "perl dies: it reads $#c, the last index of an array @c (T563).", S + 'say $s =~ /b$#c\n/x ? 1 : 0;', '$#',
  "a '$' before '#' in a pattern under /x: perl reads $#, and does not compile it (T563); put a blank between")
r('count-leading-zero', "perl dies: Invalid quantifier in {,} (T564).", S + 'say $s =~ /a{02}/ ? 1 : 0;', '{02}', ZERO)
r('count-leading-zero-second', "perl dies: Invalid quantifier in {,} (T564).", S + 'say $s =~ /a{1,03}/ ? 1 : 0;', '{1,03}', ZERO)
r('posix-without-brackets', "perl warns: POSIX syntax [: :] belongs inside character classes, and prints 1 (T565).", S + 'say $s =~ /[:alpha:]/ ? 1 : 0;', '[:', TWICE.format(':'))
r('posix-dots', "perl warns: POSIX syntax [. .] belongs inside character classes (but this one isn't implemented) (T565).", S + 'say $s =~ /[.a.]/ ? 1 : 0;', '[.', TWICE.format('.'))
r('posix-equals', "perl warns: POSIX syntax [= =] belongs inside character classes (but this one isn't implemented) (T565).", S + 'say $s =~ /[=a=]/ ? 1 : 0;', '[=', TWICE.format('='))
r('posix-one-side', "perl warns: POSIX syntax [: :] belongs inside character classes (but this one isn't fully valid) (T565).", S + 'say $s =~ /[:word]/ ? 1 : 0;', '[:', LETTERS.format(':'))
r('posix-near-miss', "perl warns: POSIX syntax [. .] belongs inside character classes (but this one isn't implemented) (T565).", S + 'say $s =~ /[.,ord]/ ? 1 : 0;', '[.', LETTERS.format('.'))
r('class-of-nothing', "perl warns: [^\\d\\D]* matches null string many times (T566).", S + 'say $s =~ /[^\\d\\D]*b/ ? 1 : 0;', '[^', EMPTY)
r('class-of-nothing-pair', "perl warns: Quantifier unexpected on zero-length expression (T566).", S + 'say $s =~ /[^\\S\\D]{2}/ ? 1 : 0;', '[^', EMPTY)
r('class-of-nothing-ranges', "perl warns: Quantifier unexpected on zero-length expression (T566).", S + 'say $s =~ /[^\\x{0}-\\x{10FFFF}]{2}/ ? 1 : 0;', '[^', EMPTY)
r('named-before-blank', "perl prints 0: the blank after \\N{U+41} is skipped, in a class (T567). The compiler printed 1.", 'my $s = " ";\nsay $s =~ /[\\N{U+41} ]/x ? 1 : 0;', '\\N', NAMED)
r('named-before-comment', "perl dies: Unmatched [ (the # after \\N{U+41} begins a comment, T567).", S + 'say $s =~ /[\\N{U+41}#]/x ? 1 : 0;', '\\N', NAMED)
r('lazy-and-wide', "perl prints 'a b' for this string and 'ab' for an equal one it keeps as UTF-8 (T569). The compiler printed 'ab'.", 'use utf8;\nmy @l = "ab" =~ /x??\\x{100}|.+/g;\nsay "@l";', '?\\x', "a lazy quantifier and a character past U+00FF in one pattern: perl 5.42's answer goes by how it happens to keep the string, a bug of its own (T569)")
r('lazy-and-wide-class', "perl prints 'a b', and 'ab' for an equal string kept as UTF-8 (T569).", 'use utf8;\nmy @l = "ab" =~ /\\w+?[\\x{100}]|.+/g;\nsay "@l";', '?[', "a lazy quantifier and a character past U+00FF in one pattern: perl 5.42's answer goes by how it happens to keep the string, a bug of its own (T569)")
NESTED = 'a count of a string, a{2}, inside a group repeated at least twice: perl 5.42 says no to strings such a pattern matches, a bug of its own (T570); write the count out, (?:aa){2}'
r('count-in-a-repeated-group', "perl prints 0, and the pattern matches: its optimiser looks for 'b&aa' two characters in (T570). The compiler printed 1.", 'say "b&aaaa" =~ /b+&(?:a{2}){2}/ ? 1 : 0;', '(?:', NESTED)
r('count-in-a-repeated-group-deep', "perl prints 0, and the pattern matches (T570). The compiler printed 1.", 'say "bbaaaaaab" =~ /b+(?:(?:a){2}){3,}./ ? 1 : 0;', '(?:', NESTED)
# ---- what breaking the rules on purpose showed no test would catch
r('count-leading-zero-first', "perl dies: Invalid quantifier in {,} (T564).", S + 'say $s =~ /a{02,3}/ ? 1 : 0;', '{02,3}', ZERO)
r('posix-escaped-twice', "perl warns: POSIX syntax [. .] belongs inside character classes (but this one isn't implemented): an escaped dot ends it (T565).", S + 'say $s =~ /[.\\.]/ ? 1 : 0;', '[.', TWICE.format('.'))
r('class-of-nothing-word', "perl warns: [^\\D\\w]+ matches null string many times (T566).", S + 'say $s =~ /[^\\D\\w]+|b/ ? 1 : 0;', '[^', EMPTY)
r('class-of-nothing-blanks', "perl warns: Quantifier unexpected on zero-length expression (T566).", S + 'say $s =~ /[^\\S\\x{9}-\\x{d} \\x{85}\\x{a0}\\x{1680}\\x{2000}-\\x{200a}\\x{2028}\\x{2029}\\x{202f}\\x{205f}\\x{3000}]{2}/ ? 1 : 0;', '[^', EMPTY)
r('count-of-a-class-in-a-repeated-group', "perl prints 0, and the pattern matches (T570).", 'say "b&aaaa" =~ /b+&(?:[a]{2}){2}/ ? 1 : 0;', '(?:', NESTED)
r('count-of-a-group-in-a-repeated-group', "perl prints 0, and the pattern matches (T570).", 'say "b&xababxabab" =~ /b+&(?:x(?:ab){2}){2}/ ? 1 : 0;', '(?:', NESTED)


def write(first):
    n = first
    for name, why, body, at, message, nth in T:
        program = f'# kind: refused\n# {why}\nuse v5.42;\n{body}\n'
        path = f't/{n}-re-{name}'
        open(path + '.pl', 'w', encoding='utf-8').write(program)
        k = program.index('use v5.42;')
        for _ in range(nth):
            k = program.index(at, k + 1)
        line = program.count('\n', 0, k) + 1
        col = len(program[program.rfind('\n', 0, k) + 1:k]) + 1
        open(path + '.expected', 'w', encoding='utf-8').write(f'{path}.pl:{line}:{col}: {message}\nexit: 1\n')
        n += 1
    return n


if __name__ == '__main__':
    if sys.argv[1] == '--perl':
        for name, why, body, at, message, nth in T:
            r_ = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', 'use v5.42;\n' + body], capture_output=True, text=True, timeout=10)
            print(f'{name}: exit {r_.returncode}; {r_.stdout!r}; {r_.stderr.strip()[:200]!r}')
    else:
        print(write(int(sys.argv[1])) - 1)
