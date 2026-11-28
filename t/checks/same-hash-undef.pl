# check: ok
# A hash made empty by undef, by name and through a reference: no order
# shows (step 16d).
use v5.42;
my %h = (pear => 3, apple => 1);
undef %h;
my %g = (fig => 2);
undef(%g);
my $r = {plum => 4};
undef %{$r};
say scalar(keys %h), scalar(keys %g);
