# check: fails: line 6: a whole hash without sort
# An undef beside the hash, not of it: the hash's order shows.
use v5.42;
my %h = (pear => 3, apple => 1);
my @l = (undef,
    %h);
say scalar(@l);
