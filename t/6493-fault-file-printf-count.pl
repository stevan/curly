# t/models/file.py 6493
# kind: fault
use v5.42;
open(my $out, '>', 'o.txt') or die "no\n";
say "before";
printf $out "%s %s\n", "one";
