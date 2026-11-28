#!/usr/bin/env python3
"""Writes the tests of the independent review of step 16d, 6260 on, from
tables written by hand, as `docs/briefs/step16d-tests.py` writes the step's
own: a `same` test's program (its .expected is perl's, from `make oracle`),
a fault test's with the text of the line it faults on, what it printed
before, and the message; a refusal's with the text its message points at
(the column is counted here) and the message. Nothing here asks the
compiler.

    python3 docs/briefs/step16d-review/reader/tests.py
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

POD = "a line that begins = and a word in the middle of a statement: perl takes it for POD only where a statement may begin, and does not compile it here"

# (number, name, kind, why, body, ...): for a fault (at, printed, message),
# for a refusal (at, message, nth).
TESTS = [
    (6260, 'review-pod-underscore', 'refused', 'perl does not compile it: syntax error near "=" (T673).',
     'say 1;\n=_x\nsay 2;\n=cut\nsay 3;', '=_x', "expected a value, found '='", 1),
    (6261, 'review-pod-after-do-block', 'refused', 'perl does not compile it: after the block of a do it looks for an operator (T674).',
     'my $i = 0;\ndo { $i++ }\n=pod\n=cut\nuntil ($i);\nsay $i;', '=pod', POD, 1),
    (6262, 'review-pod-after-map-block', 'refused', 'perl does not compile it: syntax error near "=" (T674).',
     'my @l = map {\n    $_ * 2\n}\n=pod\n=cut\n1, 2;\nsay "@l";', '=pod', POD, 1),
    (6263, 'review-pod-after-sort-block', 'refused', 'perl does not compile it: syntax error near "=" (T674).',
     'my @l = sort {\n    $a <=> $b\n}\n=pod\n=cut\n2, 1;\nsay "@l";', '=pod', POD, 1),
    (6264, 'review-pod-in-for-header', 'refused', 'perl does not compile it: syntax error near "=" (T674).',
     'my $i = 0;\nfor ($i = 0; $i < 2;\n=pod\n=cut\n$i++) { }\nsay $i;', '=pod', POD, 1),
    (6265, 'review-pod-in-blocks', 'same', 'POD where a statement may begin inside the blocks of expressions, and after an if\'s block (T674: the places that stay in).',
     'my @l = map {\n=pod\n=cut\n    my $q = $_;\n=pod\n=cut\n    $q * 2 } 1, 2;\nsay "@l";\nmy $i = 0;\ndo {\n=pod\n=cut\n    $i++;\n=pod\n=cut\n} while ($i < 2);\nsay $i;\nfor ($i = 0; $i < 2; $i++) {\n=pod\n=cut\n    say "in $i";\n}\nif ($i) { say "if"; }\n=pod\n=cut\nelse { say "else"; }\nmy $f = sub { my $v = 5;\n=pod\n=cut\n    return $v; };\nsay $f->();'),
    (6266, 'review-uc-ypogegrammeni-mark', 'fault', 'perl moves the iota past the mark: U+0301, U+0399 (T675).',
     'say "a";\nsay length uc(chr(0x345) . "a" . chr(0x301));\nmy $s = uc(chr(0x345) . chr(0x301));\nsay length $s;', 'my $s', 'a\n3\n', 'uc of U+0345 before a combining mark: perl moves it past the mark'),
    (6267, 'review-uc-ypogegrammeni-escape', 'fault', 'perl moves the iota past the mark in \\U too (T675).',
     'my $p = chr(0x345);\nmy $q = chr(0x20DD);\nsay "a";\nmy $s = "\\U$p$q\\E";\nsay length $s;', 'my $s', 'a\n', 'uc of U+0345 before a combining mark: perl moves it past the mark'),
    (6268, 'review-uc-ypogegrammeni-apart', 'same', 'U+0345 where no mark follows it, and under the functions that do not move it (T675).',
     'sub codes($s) { return join(" ", map { sprintf("%X", ord(substr($s, $_, 1))) } 0 .. length($s) - 1); }\nsay codes(uc(chr(0x345) . "a" . chr(0x345)));\nsay codes(uc(chr(0x301) . chr(0x345)));\nsay codes(uc("a" . chr(0x301) . chr(0x345) . "b" . chr(0x300)));\nsay codes(lc(chr(0x345) . chr(0x301)));\nsay codes(ucfirst(chr(0x345) . chr(0x301)));\nsay codes(lcfirst(chr(0x345) . chr(0x345)));\nsay codes(uc(chr(0x1FB3) . chr(0x301)));\nsay codes(uc(chr(0x345)) . uc(chr(0x301)));'),
    (6269, 'review-last-index-or-die', 'refused', 'perl warns: Found = in conditional, should be == (T676).',
     'my @a = (1, 2);\n$#a = 0 or die "e\\n";', 'or die', "'or die' after $#a = N: setting an array's last index is a statement alone (D251); test the array in a statement of its own", 1),
    (6270, 'review-last-index-and-die', 'refused', 'perl dies, -1 being true, and warns (T676).',
     'my @a = (1, 2);\nmy $r = \\@a;\n$r->$#* = -1 and die "e\\n";', 'and die', "'and die' after $#a = N: setting an array's last index is a statement alone (D251); test the array in a statement of its own", 1),
    (6271, 'review-case-first-in-run', 'same', 'A \\u or \\l first in a run ends with it, but for \\L\\u and \\U\\l, which perl swaps (T677).',
     'my $e = "";\nsay "\\U\\u$e\\Eabc";\nsay "\\L\\l$e\\EABC";\nsay "\\Q\\u$e\\Ea.c";\nsay "\\Q\\l$e\\EA.C";\nsay "\\L\\u$e\\Eabc";\nsay "\\U\\l$e\\EABC";\nsay "\\U\\uab\\Ecd";\nsay "\\L\\lAB\\ECD";\nsay "\\L\\uAB\\Ecd";\nsay "\\U\\lab\\ECD";\nsay "\\L\\u$e\\Eabc \\uxyz";\nsay "\\Q\\ua.b\\Ec.d";\nsay "\\U\\u$e";\nsay "\\u\\U$e\\Eabc";'),
    (6272, 'review-case-first-then-end', 'refused', 'perl prints ABC: its own answer (T677).',
     'say "\\U\\u\\Eabc";', '\\E', "\\E hard after \\u in a run: perl's answer for it is its own (T677); take the \\u out", 1),
    (6273, 'review-case-lower-first-then-end', 'refused', 'perl prints A\\.C, the run lost (T677).',
     'say "\\Q\\l\\EA.C";', '\\E', "\\E hard after \\l in a run: perl's answer for it is its own (T677); take the \\l out", 1),
]


def write():
    for number, name, kind, why, body, *rest in TESTS:
        path = f't/{number}-16d-{name}'
        full = os.path.join(ROOT, path)
        if kind == 'same':
            open(full + '.pl', 'w', encoding='utf-8').write(f'# {why}\nuse v5.42;\n{body}\n')
            continue
        program = f'# kind: {kind}\n# {why}\nuse v5.42;\n{body}\n'
        open(full + '.pl', 'w', encoding='utf-8').write(program)
        at = rest[0]
        k = program.index('use v5.42;')
        for _ in range(rest[2] if kind == 'refused' else 1):
            k = program.index(at, k + 1)
        line = program.count('\n', 0, k) + 1
        if kind == 'fault':
            printed, message = rest[1], rest[2]
            open(full + '.expected', 'w', encoding='utf-8').write(f'{printed}fault: {message} at {path}.pl line {line}.\nexit: 1\n')
        else:
            col = len(program[program.rfind('\n', 0, k) + 1:k]) + 1
            open(full + '.expected', 'w', encoding='utf-8').write(f'{path}.pl:{line}:{col}: {rest[1]}\nexit: 1\n')


if __name__ == '__main__':
    write()
    print(len(TESTS), 'tests written')
