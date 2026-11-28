# t/models/file.py 6488
# kind: fault
use v5.42;
use utf8;
open(my $out, '>', 'o.txt') or die "no\n";
print $out "plain\n";
say "before";
print $out "café\n";
say "not reached";
