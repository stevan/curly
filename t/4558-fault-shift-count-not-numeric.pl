# kind: fault
# perl warns: Argument "A" isn't numeric in left bitshift.
use v5.42;
my $y = 6 << "A";
