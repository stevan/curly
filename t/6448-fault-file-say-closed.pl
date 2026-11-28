# t/models/file.py 6448
# kind: fault
use v5.42;
open(my $out, '>', 'o.txt') or die "no\n";
close($out);
say "before";
say {$out} "y";
