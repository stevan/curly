# U+0345 where no mark follows it, and under the functions that do not move it (T675).
use v5.42;
sub codes($s) { return join(" ", map { sprintf("%X", ord(substr($s, $_, 1))) } 0 .. length($s) - 1); }
say codes(uc(chr(0x345) . "a" . chr(0x345)));
say codes(uc(chr(0x301) . chr(0x345)));
say codes(uc("a" . chr(0x301) . chr(0x345) . "b" . chr(0x300)));
say codes(lc(chr(0x345) . chr(0x301)));
say codes(ucfirst(chr(0x345) . chr(0x301)));
say codes(lcfirst(chr(0x345) . chr(0x345)));
say codes(uc(chr(0x1FB3) . chr(0x301)));
say codes(uc(chr(0x345)) . uc(chr(0x301)));
