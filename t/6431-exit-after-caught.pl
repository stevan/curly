# t/models/file.py 6431
# kind: warns
use v5.42;
sub slurp($name) { open(my $in, '<', $name) or die "no $name: $!\n"; my @l = <$in>; close($in); return @l }
try { slurp("nope.txt") } catch ($e) { print "caught: $e" }
die "after a caught one\n";
