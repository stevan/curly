# kind: refused
# perl runs it: '1\n'.
use v5.42;
my $h = {a => 1};
say %{$h}{"a"};
