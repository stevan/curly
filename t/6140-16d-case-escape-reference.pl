# kind: fault
# perl uppercases the reference's address.
use v5.42;
my $r = [1];
say "\L$r";
