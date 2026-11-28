# t/models/file.py 6455
# kind: fault
use v5.42;
open(my $out, '>', 'o.txt') or die "no\n";
print $out "x\n";
say "before";
open(my $in, '<', 'o.txt');
say "not reached";
