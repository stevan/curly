"""Ways out of a lone range's loop inside a loop that froze (D259): what
was frozen is given back once, and what was never frozen is not."""
import itertools

OUTS = ['next OUT;', 'last OUT;', 'next;', 'last;', 'return 5;', 'die "d\\n";', '$i < 1 or next OUT;', '$i and last OUT;', 'next OUT if $i;', '']
INNERS = ['for my $i (0 .. $#b) { %s }', 'for my $i (0 .. $#a) { %s }', 'for my $i (@b) { %s }', 'for my $i (0 .. $#b, 9) { %s }', '{ my $i = 0; do { $i++; %s } while ($i < 2); }',
          'for my $i (0 .. 1) { for my $j (@b) { %s } }', 'for my $i (@b) { for my $j (0 .. $#a) { %s } }', 'my @q = map { my $i = $_; for my $j (0 .. $#b) { %s } 1 } 1, 2;']
OUTERS = ['for my $x (@a)', 'for my $x (0 .. $#a)', 'for my $x (values %h)', 'for my $x (reverse 0 .. $#a)']


def cases():
    n = 0
    for outer, inner, out in itertools.product(OUTERS, INNERS, OUTS):
        n += 1
        body = inner % out
        prog = ('my @a = (1, 2); my @b = (3, 4); my %%h = (k => 1); my $c = 0;\n'
                'sub run() { OUT: %s { $c++; %s $c++; } return 0; }\n'
                'try { say "r", run(); } catch ($e) { print "c$e"; }\n'
                'push @a, 7; push @b, 8; $h{n} = 2; $#a = 1; undef @b; say "c$c a@a b@b ", scalar(%%h);\n'
                'try { say "r", run(); } catch ($e) { print "c$e"; }\n'
                'for my $y (@a, @b, values %%h) { $c++; } push @a, 1; push @b, 1; delete $h{k}; say "c$c a@a b@b ", scalar(%%h);\n') % (outer, body)
        yield ('w%03d' % n, prog)
