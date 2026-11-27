# kind: refused
# perl warns: Useless use of private variable in void context.
use v5.42;
my $r = [1, 2];
my $s = [3];
my @c = @{$r, $s};
