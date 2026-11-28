use v5.42;
open(my $fh, '<', 'nope.txt') or die "cannot: $!";
