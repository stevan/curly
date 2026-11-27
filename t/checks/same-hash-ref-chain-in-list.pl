# check: fails: line 5: a whole hash without sort
# A hash through a chain in a list (step 13b).
use v5.42;
my $r = {x => [{y => 1}]};
say join ",", $r->{x}[0]->%*;
