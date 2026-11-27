#!/usr/bin/env python3
# Writes step 19's refusal tests from a table written by hand: the program,
# the text the message points at (its column is counted here, from the
# program's own text), and the message. Nothing here asks the compiler.
# What perl does with each is in its comment, from perl 5.42 run plain
# (`python3 docs/briefs/step19-refusals.py --perl` prints each again).
#
#     python3 docs/briefs/step19-refusals.py 5400
import subprocess
import sys
T = []
def r(name, why, body, at, message, nth=1):
    T.append((name, why, body, at, message, nth))

S = 'my $s = "ab";\n'
GROUP_IN_REPEAT = 'a group that captures inside a repeated group: perl keeps or forgets its value by rules of its own (D231, T540); capture the whole repeat, ((?:...)*)'
NULLABLE = 'a quantifier on what can match the empty string: perl warns, or stops by rules of its own (D231, T552)'
DOLLAR = "a '$' in a pattern that is not at its end, or before ')' or '|': perl may take it for a variable (D229, T550); write \\$ for the character"
ICASE = "a character past ASCII in a pattern under /i: perl folds it by Unicode's tables, one character to two (D230, T546)"
LATER = '{} is not in the language yet (D226)'

# ---- where a pattern may stand (D234)
r('alone', "perl runs it: '1' if $_ matches.", 'for ("a") {\n    say /a/ ? 1 : 0;\n}', '/a/', 'a pattern alone matches $_: write $_ =~ /.../, or the variable it is for (D234, D85)')
r('alone-in-grep', "perl runs it: 'a'.", 'my @l = grep { /a/ } ("a", "b");', '/a/', 'a pattern alone matches $_: write $_ =~ /.../, or the variable it is for (D234, D85)')
r('bang-before', "perl warns: Possible precedence problem between ! and pattern match (T547).", S + 'say !$s =~ /a/ ? 1 : 0;', '!$s', "'!' before the left side of '=~': perl warns of a precedence problem, and applies it first (T547); write !(... =~ ...), or (!...) =~ ...")
r('array-on-the-left', "perl warns: Applying pattern match (m//) to @a will act on scalar(@a) (T547).", 'my @a = (1);\nsay @a =~ /1/ ? 1 : 0;', '=~', "more than one value on the left of '=~': perl matches one value, a count or the last (T547)")
r('hash-on-the-left', "perl warns: Applying pattern match (m//) to %h will act on scalar(%h).", 'my %h = (a => 1);\nsay %h =~ /1/ ? 1 : 0;', '=~', "a hash on the left of '=~': perl matches one value, a count or the last (T547)")
r('list-on-the-left', "perl warns: Useless use of a constant in void context; it matches the last.", 'my $r = ("a", "b") =~ /b/;', '=~', "a list on the left of '=~': perl matches one value, a count or the last (T547)")
r('string-on-the-right', "perl runs it: the string is a pattern, '1'.", S + 'say $s =~ "a" ? 1 : 0;', '"a"', "the right side of '=~' is a pattern, /.../ or m{...}: anything else is matched as a pattern made as the program runs, which is cut (D229)")
r('variable-on-the-right', "perl runs it: the variable is a pattern.", S + 'my $p = "a";\nsay $s =~ $p ? 1 : 0;', '$p ?', "the right side of '=~' is a pattern, /.../ or m{...}: anything else is matched as a pattern made as the program runs, which is cut (D229)")
r('substitution', "perl runs it.", S + '$s =~ s/a/b/;', 's/', 's/// is not in the language yet (step 20)')
r('empty-pattern', "perl matches the last pattern that matched (T66).", S + 'say $s =~ // ? 1 : 0;', '/ ?', 'the empty pattern: perl matches the last pattern that matched (T66)')
r('g-where-one-value', "perl runs it, and sets pos($s) (T543).", S + 'say(($s =~ /a/g) ? 1 : 0);', '=~', 'a match under /g where one value is wanted: perl goes on from where the last one left off (pos), which is cut (D233, T543); take the matches as a list')
r('g-in-a-while', "perl runs it: 'a', 'b' (T543).", S + 'while ($s =~ /(\\w)/g) {\n    last;\n}', '=~', 'a match under /g where one value is wanted: perl goes on from where the last one left off (pos), which is cut (D233, T543); take the matches as a list')
r('g-with-not', "perl runs it: '0'.", S + 'say $s !~ /a/g ? 1 : 0;', 'g ?', "/g with '!~': perl ignores it there, or goes on from where the last match left off (D233)")
r('dollar-one', "perl runs it: 'a' (T554).", S + 'if ($s =~ /(a)/) {\n    say $1;\n}', '$1', "$1, a variable a match sets, is not in the language: a match where a list is wanted gives what it captured, my ($x) = $s =~ /(...)/; (D228, T554)")
r('dollar-ampersand', "perl runs it: 'a'.", S + 'if ($s =~ /a/) {\n    say $&;\n}', '$&', "$&, a variable a match sets, is not in the language: a match where a list is wanted gives what it captured, my ($x) = $s =~ /(...)/; (D228, T554)")
# ---- the delimiters (D227)
r('bang-delimiter', "perl runs it: '1'.", S + 'say $s =~ m!a! ? 1 : 0;', 'm!', "m!...: a pattern's delimiters are '/' and, after m, a bracket hard against it (D227, T541): m{...}")
r('bar-delimiter', "perl runs it: '1': the escaped | is alternation (T541).", S + 'say $s =~ m|a\\|x| ? 1 : 0;', 'm|', "m|...: a pattern's delimiters are '/' and, after m, a bracket hard against it (D227, T541): m{...}")
r('pattern-never-ends', "perl does not compile it: Search pattern not terminated.", S + 'say $s =~ /a;', '/a;', 'a pattern that never ends: it begins here')
# ---- a variable in a pattern (D229)
r('variable-in-pattern', "perl runs it, the variable interpolated (T550).", S + 'my $x = "a";\nsay $s =~ /$x/ ? 1 : 0;', '$x/', DOLLAR)
r('dollar-in-the-middle', "perl takes $b for the variable $b.", S + 'say $s =~ /a$b/ ? 1 : 0;', '$b', DOLLAR)
r('array-in-pattern', "perl interpolates @a.", S + 'my @a = ("a");\nsay $s =~ /@a/ ? 1 : 0;', '@a/', "'@' in a pattern: perl may take it for an array (D229); write \\@")
r('dollar-in-class', "perl takes $] for its version, and dies: Unmatched [.", S + 'say $s =~ /[$]/ ? 1 : 0;', '$]', "'$' in a class: perl may take it for a variable (D229); write \\$")
r('quote-escape', "perl runs it.", S + 'say $s =~ /\\Qa.\\E/ ? 1 : 0;', '\\Q', '\\Q in a pattern: the case escapes, and \\Q...\\E, are not in the language (D229)')
# ---- the flags (D226)
r('flag-unknown', "perl does not compile it: Unknown regexp modifier.", S + 'say $s =~ /a/q ? 1 : 0;', 'q ?', "'q' after a pattern is no flag of perl's: perl does not compile it")
r('flag-later', "perl runs it.", S + 'say $s =~ /a/a ? 1 : 0;', 'a ?', 'the flag /a is not in the language (D226)')
r('flag-twice', "perl runs it.", S + 'say $s =~ /a/ii ? 1 : 0;', 'ii', '/i given twice')
r('flag-xx', "perl runs it: /xx, blanks in classes ignored too.", S + 'say $s =~ /a/xx ? 1 : 0;', 'xx', '/xx in a pattern is not in the language')
r('flag-e', "perl does not compile it on a match: Unknown regexp modifier.", S + 'say $s =~ /a/e ? 1 : 0;', 'e ?', 'the flag /e, which is s///e is not in the language (D226)')
# ---- what perl warns of or dies at
r('unknown-escape', "perl warns: Unrecognized escape \\y passed through.", S + 'say $s =~ /a\\yb/ ? 1 : 0;', '\\y', "\\y in a pattern is no escape of perl's: perl warns that it passes it through, or does not compile it")
r('octal-zero', "perl runs it: NUL.", S + 'say $s =~ /\\0/ ? 1 : 0;', '\\0', '\\0 in a pattern is octal to perl: write \\x00')
r('two-digit-backreference', "perl dies: Reference to nonexistent group.", S + 'say $s =~ /(a)\\12/ ? 1 : 0;', '\\12', 'a backreference of two digits is octal to perl or another group: \\1 to \\9 are in (D226)')
r('backreference-to-nothing', "perl does not compile it: Reference to nonexistent group (T551).", S + 'say $s =~ /(a)\\2/ ? 1 : 0;', '\\2', '\\2 names a group the pattern does not have, or not yet: perl does not compile it (T551)')
r('backreference-inside', "perl runs it: no match.", S + 'say $s =~ /(a\\1)/ ? 1 : 0;', '\\1', '\\1 inside the group it names: write it after the group closes')
r('nested-quantifiers', "perl does not compile it: Nested quantifiers.", S + 'say $s =~ /a**/ ? 1 : 0;', '*/', 'a quantifier after a quantifier: perl does not compile it (Nested quantifiers); bracket the first, (?:...)')
r('quantifier-first', "perl does not compile it: Quantifier follows nothing.", S + 'say $s =~ /*a/ ? 1 : 0;', '*a', 'a quantifier with nothing before it: perl does not compile it')
r('backwards-count', "perl warns: Quantifier {n,m} with n > m can't match.", S + 'say $s =~ /a{2,1}/ ? 1 : 0;', '{2', '{n,m} with n greater than m: perl warns that it cannot match')
r('count-too-large', "perl runs it.", S + 'say $s =~ /a{40000}/ ? 1 : 0;', '{4', 'a count past 32766 in a pattern (D236)')
r('count-blanks', "perl runs it: '1' for 'aa' (T542).", S + 'say $s =~ /a{ 2 }/ ? 1 : 0;', '{ 2', "blanks in a quantifier's braces: perl 5.42 takes them (D236, T542); write them hard together")
r('count-no-least', "perl runs it: {,3} is {0,3} (T542).", S + 'say $s =~ /a{,3}/ ? 1 : 0;', '{,', '{,n} in a pattern is {0,n} to perl 5.42: write {0,n} (D236, T542)')
r('brace-alone', "perl warns: Unescaped left brace in regex is passed through (T542).", S + 'say $s =~ /a{b/ ? 1 : 0;', '{b', "a '{' in a pattern that is no quantifier's: perl warns, or passes it through; write \\{")
r('close-brace-alone', "perl runs it: a literal }.", S + 'say $s =~ /a}/ ? 1 : 0;', '}/', "a '}' in a pattern: write \\}")
r('lazy-exact-count', "perl warns: Useless use of greediness modifier '?'.", S + 'say $s =~ /a{2}?/ ? 1 : 0;', '?/', "a ? after {2}: perl warns that it is a useless greediness modifier")
r('range-backwards', "perl does not compile it: Invalid [] range.", S + 'say $s =~ /[z-a]/ ? 1 : 0;', 'a]', 'a range backwards, z-a: perl does not compile it')
r('range-of-a-class', "perl warns: False [] range.", S + 'say $s =~ /[a-\\d]/ ? 1 : 0;', 'a-', "a range with one of perl's classes at an end: perl warns, False [] range; write the - as \\-")
r('dash-dash-first-in-class', "perl dies: Invalid [] range, a range from - to the newline (found by briefs/step19-review/patterns.py).", S + 'say $s =~ /[--\\n]/ ? 1 : 0;', '--', "'--' first in a class: perl reads a range from '-' there; write \\-")
r('bracket-first-in-class', "perl runs it: ] is in the class.", S + 'say $s =~ /[]a]/ ? 1 : 0;', ']a]', "']' first in a class: perl takes it for a character of the class; write \\]")
r('posix-class', "perl runs it: [:alpha:].", S + 'say $s =~ /[[:alpha:]]/ ? 1 : 0;', '[:', "'[' in a class: perl may take it for a POSIX class, [:alpha:]; write \\[")
r('class-never-ends', "perl does not compile it: Unmatched [.", S + 'say $s =~ /[ab/ ? 1 : 0;', '[ab', "a '[' with no ']' after it in the pattern: perl does not compile it")
r('paren-never-ends', "perl does not compile it: Unmatched (.", S + 'say $s =~ /(ab/ ? 1 : 0;', '(ab', "a '(' with no ')' after it in the pattern: perl does not compile it")
r('paren-never-opens', "perl does not compile it: Unmatched ).", S + 'say $s =~ /ab)/ ? 1 : 0;', ')/', "a ')' with no '(' before it in the pattern: perl does not compile it")
r('backspace-in-class', "perl runs it: \\b in a class is a backspace.", S + 'say $s =~ /[\\b]/ ? 1 : 0;', '\\b]', '\\b in a class is a backspace to perl: write \\x08')
r('x-alone', "perl runs it: \\x alone is a NUL.", S + 'say $s =~ /\\x/ ? 1 : 0;', '\\x', '\\x with no hex digit after it: perl reads it as a NUL; write \\x00 or \\x{...}')
# ---- D231
r('quantified-star', "perl warns: matches null string many times (T552).", S + 'say $s =~ /(?:a*)*/ ? 1 : 0;', '*/', NULLABLE)
r('quantified-anchor', "perl warns: matches null string many times (T552).", S + 'say $s =~ /(?:\\b)+/ ? 1 : 0;', '+/', NULLABLE)
r('quantified-optional-group', "perl runs it: $1 is the empty string (T553).", S + 'my @l = ($s =~ /(a*)?b/);', '?b', NULLABLE)
r('capture-in-repeat', "perl runs it: $1 undef (T540).", S + 'my @l = ($s =~ /(?:(a)|b)*/);', '(?:', GROUP_IN_REPEAT)
r('capture-in-capture-repeat', "perl runs it.", S + 'my @l = ($s =~ /((a)b)+/);', '((a', GROUP_IN_REPEAT)
# ---- D230
r('icase-past-ascii', "perl runs it, folding by Unicode's tables (T546).", 'use utf8;\nmy $s = "x";\nsay $s =~ /é/i ? 1 : 0;', 'é/', ICASE)
# ---- D237
r('wide-blank', "perl's /x takes U+2028 for a blank.", 'use utf8;\nmy $s = "x";\nsay $s =~ /a b/ ? 1 : 0;', ' ', "U+2028 in a pattern: perl's /x takes it for a blank (D237); write it as \\x{2028}")
# ---- not in the subset yet (D226)
r('lookahead', "perl runs it.", S + 'say $s =~ /a(?=b)/ ? 1 : 0;', '(?=', LATER.format('lookaround'))
r('named-capture', "perl runs it.", S + 'my @l = ($s =~ /(?<x>a)/);', '(?<', LATER.format('a named capture'))
r('inline-flags', "perl runs it.", S + 'say $s =~ /(?i)A/ ? 1 : 0;', '(?i', '(?...) is not in the language: of its forms, (?:...) is (D226)')
r('comment-group', "perl runs it.", S + 'say $s =~ /a(?#c)b/ ? 1 : 0;', '(?#', '(?#...) is not in the language: under /x a comment is # to the end of the line')
r('possessive', "perl runs it.", S + 'say $s =~ /a++/ ? 1 : 0;', '+/', LATER.format('a possessive quantifier'))
r('property', "perl runs it.", S + 'say $s =~ /\\p{L}/ ? 1 : 0;', '\\p', '\\p{...}, a Unicode property, is not in the language yet (D226)')
r('keep', "perl runs it.", S + 'say $s =~ /a\\Kb/ ? 1 : 0;', '\\K', LATER.format('\\K in a pattern'))
r('named-backreference', "perl runs it.", S + 'say $s =~ /(a)\\g1/ ? 1 : 0;', '\\g', '\\g, a backreference by a number in braces or by a name, is not in the language yet: write \\1 to \\9 (D226)')

# ---- step 20's, refused as the word (found by the census: son-audit/f/b13.pl)
r('transliteration', "perl runs it: 'bb'.", S + '$s =~ tr/a/b/;', 'tr/', 'tr/// is not in the language yet (step 20)')
r('substitution-alone', "perl runs it on $_.", 'for my $x ("a") {\n    my @l = map { s/a/b/r } ($x);\n}', 's/', 's/// is not in the language yet (step 20)')


def write(first, table=None):
    n = first
    for name, why, body, at, message, nth in (T if table is None else table):
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
        import os
        for name, why, body, at, message, nth in T:
            r_ = subprocess.run([os.environ.get('CURLY_PERL', 'perl'), '-e', 'use v5.42;\n' + body], capture_output=True, text=True, timeout=10)
            print(f'{name}: exit {r_.returncode}; {r_.stdout!r}; {r_.stderr.strip()[:200]!r}')
    else:
        print(write(int(sys.argv[1])) - 1)
