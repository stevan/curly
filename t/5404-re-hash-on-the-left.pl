# kind: refused
# perl warns: Applying pattern match (m//) to %h will act on scalar(%h).
use v5.42;
my %h = (a => 1);
say %h =~ /1/ ? 1 : 0;
