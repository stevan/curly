# kind: refused
# perl runs it: '1'.
use v5.42;
my $f = sub { wantarray };
my @l = $f->();
say @l;
