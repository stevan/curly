# kind: refused
# perl does not compile it: Can't use 'defined(%hash)'.
use v5.42;
my $h = {a => 1};
say defined(%{$h});
