# kind: fault
# perl dies: not a HASH reference (T203). A fault since step 13d, which takes the chain in.
use v5.42;
my $x = 3;
say "$x->{a}";
