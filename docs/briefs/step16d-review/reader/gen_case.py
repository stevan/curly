"""uc, lc, ucfirst, lcfirst, quotemeta and the case escapes over strings
dense with the characters whose neighbours could matter (D256, D257):
U+0345 and the marks round it, sigmas, the letters that map to several."""
import random

POOL = [0x345, 0x345, 0x345, 0x300, 0x301, 0x315, 0x316, 0x361, 0x20DD, 0x1D165, 0x483, 0x93C, 0xFE00, 0x200D, 0xAD,
        0x41, 0x61, 0x20, 0x2E, 0x3B1, 0x391, 0x399, 0x3B9, 0x1FB3, 0x1FBC, 0x1F80, 0x1FB7, 0x390, 0x3A3, 0x3C2, 0x3C3,
        0xDF, 0x130, 0x131, 0x69, 0x49, 0x307, 0x1C4, 0x1C5, 0x1C6, 0xFB03, 0x149, 0x1E9E, 0x10400, 0x10428, 0x2126, 0x1F88]

FUNCS = ['uc', 'lc', 'ucfirst', 'lcfirst', 'quotemeta']


def lit(cps):
    return '"' + ''.join('\\x{%X}' % c for c in cps) + '"'


def show(expr):
    return 'say join(" ", map { sprintf("%%X", ord($_)) } split_chars(%s));' % expr


HELP = 'sub split_chars($s) { my @c; for my $i (0 .. length($s) - 1) { push @c, substr($s, $i, 1); } return @c; }\n'


def cases():
    rnd = random.Random(1606)
    for n in range(260):
        lines = [HELP]
        for _ in range(12):
            cps = [rnd.choice(POOL) for _ in range(rnd.randrange(1, 7))]
            f = rnd.choice(FUNCS)
            k = rnd.randrange(6)
            if k < 3:
                lines.append(show('%s(%s)' % (f, lit(cps))))
            elif k == 3:
                esc = rnd.choice(['\\U', '\\L', '\\Q', '\\u', '\\l', '\\u\\L', '\\L\\u', '\\U\\l'])
                body = ''.join('\\x{%X}' % c for c in cps)
                lines.append(show('"%s%s"' % (esc, body)))
            elif k == 4:
                cut = rnd.randrange(len(cps) + 1)
                lines.append('{ my $p = %s; my $q = %s; %s %s }' % (lit(cps[:cut]), lit(cps[cut:]), show('"\\U$p$q\\E"'), show('uc($p . $q)')))
            else:
                cut = rnd.randrange(len(cps) + 1)
                lines.append('{ my $p = %s; %s }' % (lit(cps[:cut]), show('"\\U$p\\E%s"' % ''.join('\\x{%X}' % c for c in cps[cut:]))))
        yield ('c%03d' % n, '\n'.join(lines) + '\n')
