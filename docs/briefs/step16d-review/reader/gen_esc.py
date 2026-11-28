"""Random strings of the case escapes, text, variables and other escapes
(D256), in double quotes, qq and heredocs, a string to a line; and substr
of four over every offset and length (D254)."""
import random

PIECES = ['\\U', '\\L', '\\Q', '\\E', '\\u', '\\l', '\\E', '\\U', 'ab', 'CD', 'e.F', ' ', '$x', '${y}', '@a', '$a[0]', '$h{k}', '$r->[1]', '$r->@*', '\\n', '\\t', '\\\\', '\\$', '\\@', '\\"', 'é', 'ß', '\\x41', '\\x{e9}', '.', '-', '_', '9',
          '\\F', '\\N{U+E9}', '\\e', '\\0', '$#a', '@{[ 1 ]}', '\\Q', '\\u', '\\l', '$e', '\\101', '\\cA', '{', '}', '(', ')', '[0]', '{k}', '->[0]', '::', "'"]
PRE = 'my $x = "xY.z"; my $y = "Wv"; my @a = ("a1", "B.2"); my %h = (k => "hK"); my $r = ["r0", "R.1"]; my $e = "";\n'


def cases():
    rnd = random.Random(256)
    for n in range(350):
        lines = []
        for _ in range(4):
            body = ''.join(rnd.choice(PIECES) for _ in range(rnd.randrange(1, 7)))
            form = rnd.randrange(8)
            if form < 5:
                lines.append('say "%s";' % body)
            elif form == 5:
                lines.append('say qq{%s};' % body)
            elif form == 6:
                lines.append('print <<END;\n%s\nEND' % body)
            else:
                lines.append('say "<" . "%s" . ">";' % body)
        # each line a program of its own: one refusal must not hide the rest
        for k, line in enumerate(lines):
            yield ('e%03d%d' % (n, k), PRE + line + '\n')
    yield from substr_cases()


def substr_cases():
    rnd = random.Random(254)
    strings = ['"abcd"', '""', '"é1ß2"', '12345', '"a"']
    n = 0
    for s in strings:
        lines = []
        for off in range(-7, 8):
            for length in range(-7, 8):
                lines.append('{ my $s = %s; substr($s, %d, %d, "<>"); say "%d %d [$s]"; }' % (s, off, length, off, length))
        # a line a program where it may fault, in blocks of nine where it does not: perl is asked each alone below
        for line in lines:
            n += 1
            if n % 3 == 0:
                yield ('b%04d' % n, line + '\n')
