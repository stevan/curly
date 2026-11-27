# kind: refused
# perl runs it, and says nothing.
use v5.42;
my $r = [1, 2];
sub grow() {
    push $r->@*, 3;
    return 1;
}
my $s = $r->[0] . grow();
