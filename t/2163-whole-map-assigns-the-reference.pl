# kind: refused
# perl crashes: a segmentation fault (T342).
use v5.42;
my $r = [1, 2];
my @m = map { $r = [7]; $_ } @{$r};
