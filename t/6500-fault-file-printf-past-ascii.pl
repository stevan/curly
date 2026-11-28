# t/models/file.py 6500
# kind: fault
use v5.42;
use utf8;
open(my $out, '>', 'o.txt') or die "no\n";
say "before";
printf $out "%s\n", "café";
say "not reached";
