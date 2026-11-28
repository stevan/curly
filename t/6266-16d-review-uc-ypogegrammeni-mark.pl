# kind: fault
# perl moves the iota past the mark: U+0301, U+0399 (T675).
use v5.42;
say "a";
say length uc(chr(0x345) . "a" . chr(0x301));
my $s = uc(chr(0x345) . chr(0x301));
say length $s;
