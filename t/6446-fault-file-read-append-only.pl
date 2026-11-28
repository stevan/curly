# t/models/file.py 6446
# kind: fault
use v5.42;
open(my $out, '>>', 'o.txt') or die "no\n";
say "before";
my @l = <$out>;
