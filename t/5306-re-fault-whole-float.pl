# kind: fault
# perl matches "1e+15", which a number of the same value written 1e15 + 0
# does not print (D36).
use v5.42;
my @l = (1e15 =~ /(e)/);
say scalar(@l);
