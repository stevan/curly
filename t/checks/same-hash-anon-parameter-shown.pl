# check: fails: keys without sort
# The same sub, whose body prints the hash's keys in perl's order.
use v5.42;
my $f = sub (%o) { return join(",", keys %o) };
say $f->(a => 1, b => 2, c => 3);
