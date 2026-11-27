# check: fails: line 5: a whole hash without sort
# The same with braces (step 13b).
use v5.42;
my $h = {a => 1};
my @l = (%{$h}, 1);
say "@l";
