# kind: refused
# perl prints 'a b' for this string and 'ab' for an equal one it keeps as UTF-8 (T569). The compiler printed 'ab'.
use v5.42;
use utf8;
my @l = "ab" =~ /x??\x{100}|.+/g;
say "@l";
