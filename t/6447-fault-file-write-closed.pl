# t/models/file.py 6447
# kind: fault
use v5.42;
open(my $out, '>', 'o.txt') or die "no\n";
print $out "x";
close($out);
say "before";
print $out "y";
