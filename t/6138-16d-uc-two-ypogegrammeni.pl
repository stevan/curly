# kind: fault
# perl makes one capital iota of the two (T664): 1 character.
use v5.42;
say "a";
my $s = uc(chr(0x345) . chr(0x345));
say length $s;
