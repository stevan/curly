# kind: refused
# perl prints 'a b', and 'ab' for an equal string kept as UTF-8 (T569).
use v5.42;
use utf8;
my @l = "ab" =~ /\w+?[\x{100}]|.+/g;
say "@l";
