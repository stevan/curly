# kind: refused
# perl dies, -1 being true, and warns (T676).
use v5.42;
my @a = (1, 2);
my $r = \@a;
$r->$#* = -1 and die "e\n";
