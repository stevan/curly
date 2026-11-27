# kind: fault
# perl dies: Can't use string ("1") as an ARRAY ref (T227). A fault since step 13d, which takes the chain in.
use v5.42;
my %h = (a => 1, b => 2, c => 3, d => 4);
say "$h{a}[0]";
