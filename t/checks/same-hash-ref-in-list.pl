# check: fails: line 6: a whole hash without sort
# A hash through a reference in a list is its keys and values in perl's
# order (step 13b).
use v5.42;
my $h = {a => 1};
say join ",", $h->%*;
