# The census reading's statements about perl (docs/briefs/census-open/
# README.md), as claims.py's rows. claims.py reads it.
#
#     python3 docs/briefs/claims.py census-scalar census-last-index
def c(id, where, code, **said):
    return (id, where, code, said)

W = 'census-open/README.md'
CENSUS = [
    c('census-scalar', W, 'my @a = (1,2,3); my %h = (a=>1, b=>2); my $r = [4,5]; print scalar @a + 1, "|", scalar @a == 3 ? "y" : "n", "|", scalar @a, "|", scalar @{$r}, "|", scalar %h, "|", scalar keys %h, "\\n";', out='4|y|3|2|2|2\n'),
    c('census-scalar-ops', W, 'my @a = (1,2,3); print scalar @a . "x", "|", scalar @a x 2, "|", scalar @a < 4, "\\n"; my @b = (scalar @a, 9); print "@b\\n";', out='3x|33|1\n3 9\n'),
    c('census-last-index', W, 'my @a=(1,2,3); $#a = 1; print "@a|", scalar(@a), "\\n"; $#a = 3; print scalar(@a), defined $a[3] ? "d":"u", exists $a[3] ? "e":"n", "\\n"; $#a = -1; print scalar(@a), "\\n"; $#a = 1.7; print scalar(@a), "\\n"; $#a = "2"; print scalar(@a), "\\n";', out='1 2|2\n4un\n0\n2\n3\n'),
    c('census-last-index-negative', W, 'my @a=(1); $#a = -2; print scalar(@a); $#a = 0; $#a = -5; print scalar(@a), "\\n";', out='00\n'),
    c('census-last-index-undef', W, 'my @a=(1); my $u; $#a = $u; print scalar(@a), "\\n";', out='1\n', err='Use of uninitialized value'),
    c('census-do-while-last', W, 'my $i=0; for my $k (1..3) { do { $i++; last if $i == 2 } while ($i < 5); print "k$k\\n" } print "$i\\n";', out='2\n'),
    c('census-do-until', W, 'my $i=0; do { $i++ } until $i >= 3; print "$i\\n";', out='3\n'),
    c('census-do-if', W, 'my $x=1; my $u = do { if ($x>2) { "a" } }; print defined $u ? "d[$u]" : "u", "\\n";', out='d[]\n'),
    c('census-do-list', W, 'my $s = do { (4,5,6) }; print "$s\\n";', out='6\n', err='Useless use of a constant'),
    c('census-do-one', W, 'my $c = do { 1; 2 }; print "$c\\n";', out='2\n'),
    c('census-do-late', W, 'my $x=1; my @l=($x, do { $x=7 }); print "@l\\n";', out='7 7\n'),
    c('census-undef', W, 'my @a=(1,2,3); undef @a; print scalar(@a),"\\n"; my %h=(a=>1); undef %h; print scalar(%h),"\\n"; my $x=5; my $r = undef $x; print defined $x ? "d":"u", defined $r ? "d":"u", "\\n";', out='0\n0\nuu\n'),
    c('census-holes', W, 'my @a; $a[5]=1; print exists $a[2] ? "e":"n", exists $a[5] ? "e":"n", scalar(@a), "\\n"; my @b=(1,2,3); delete $b[2]; print scalar(@b), "\\n"; delete $b[0]; print scalar(@b), exists $b[0] ? "e":"n", "\\n";', out='ne6\n2\n2n\n'),
    c('census-shift-missing', W, 'sub g { my $x = shift; defined $x ? $x : "u" } print g(), g(5, 6), "\\n";', out='u5\n'),
    c('census-signature-missing', W, 'sub g($x, @) { $x } print g(), "\\n";', exit=255, err='Too few arguments for subroutine'),
]
