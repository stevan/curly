# What an uncaught die exits with (D272) after every sequence, up to three long and a sample of longer ones, of the
# things that touch a file or stdin, over three files. A die caught and a string made of $! in between change nothing.
import itertools, random, os
OPS = {
 'R': "$l = <$h>;", 'L': "@l = <$h>;", 'E': "$e = eof($h);", 'F': "open($n, '<', 'nope.txt');", 'O': "open($k, '<', 'in.txt');", 'C': "close($h); open($h, '<', $name) or die \"re\\n\";",
 'S': "$l = <STDIN>;", 'T': "$e = eof(STDIN);", 'A': "@l = <STDIN>;", 'W': "open($w, '>', 'o.txt'); print $w 'x';", 'X': "close($w) if defined($w);", 'D': "open($n, '>', '.');",
 'P': "print 'p';", 'Y': "try { die \"c\\n\" } catch ($x) { }", 'K': "close($k) if defined($k);", 'M': "{ open(my $t, '<', $name) or die \"t\\n\"; my @x = <$t>; }", 'Q': "{ open(my $t, '<', $name) or die \"t\\n\"; }",
}
HEAD = "my ($l, @l, $e, $n, $k, $w); my $name = '%s'; open(my $h, '<', $name) or die \"no\\n\";\n"
def prog(seq, name, end):
    return HEAD % name + '\n'.join(OPS[c] for c in seq) + '\n' + end
CASES = []
core = 'RLEFOCST'
r = random.Random(21)
which = os.environ.get('PART', 'short')
if which == 'short':
    for n in (1, 2, 3):
        for seq in itertools.product(core, repeat=n):
            for name in ('in.txt', 'empty.txt', 'nonl.txt'):
                if n == 3 and name == 'nonl.txt': continue
                CASES.append({'p': prog(seq, name, 'die "x\\n";'), 'stdin': b's1\n'})
else:
    for i in range(1500):
        seq = [r.choice(list(OPS)) for _ in range(r.randint(4, 9))]
        CASES.append({'p': prog(seq, r.choice(['in.txt', 'empty.txt', 'nonl.txt', 'zero.txt']), r.choice(['die "x\\n";', 'die "x\\n";', 'die "x\\n";', 'die "x";', 'warn "w"; die "x\\n";', 'if (!open($n, \'<\', \'nope.txt\')) { die "x: $!\\n"; }'])), 'stdin': r.choice([b'', b's1\n', b's1\ns2'])})
