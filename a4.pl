use v5.42;
open(my $fh, '<', 'in.txt') or die "cannot: $!";
my $l = <$fh>; close($fh);
die "x";
