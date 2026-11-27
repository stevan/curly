# perl prints 1; in the language since step 13d.
use v5.42;
my $r = [1];
say qq{$r->[0]};
