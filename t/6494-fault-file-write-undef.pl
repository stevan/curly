# t/models/file.py 6494
# kind: fault
use v5.42;
open(my $out, '>', 'o.txt') or die "no\n";
my $u;
say "before";
print $out "a", $u;
