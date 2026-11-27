# kind: refused
# perl runs it: 'yes', and warns: Found = in conditional.
use v5.42;
my %h;
$h{a} = 3 and say "yes";
