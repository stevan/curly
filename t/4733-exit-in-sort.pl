# t/models/io.py 4733
use v5.42;
my @s = sort { exit 6 if $a eq "c"; $a cmp $b } ("b", "a", "c");
say "no";
