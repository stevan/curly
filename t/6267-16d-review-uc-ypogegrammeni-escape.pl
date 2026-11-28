# kind: fault
# perl moves the iota past the mark in \U too (T675).
use v5.42;
my $p = chr(0x345);
my $q = chr(0x20DD);
say "a";
my $s = "\U$p$q\E";
say length $s;
