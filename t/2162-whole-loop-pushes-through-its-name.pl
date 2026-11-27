# kind: refused
# perl runs it, and says nothing.
use v5.42;
my $r = [1, 2];
for my $x ($r->@*) {
    push $r->@*, 3;
    last;
}
