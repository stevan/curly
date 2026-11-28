# kind: refused
# perl runs it in silence: refused with && and ||, the reviewer's default (D222).
use v5.42;
my $l;
my $x = ($l = <STDIN>) // "f";
