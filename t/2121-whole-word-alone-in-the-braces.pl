# kind: refused
# perl runs it: '1\n' (@{true} is @true).
use v5.42;
my @true = (1);
say scalar(@{true});
