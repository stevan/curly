# kind: refused
# perl runs it: '1': the escaped | is alternation (T541).
use v5.42;
my $s = "ab";
say $s =~ m|a\|x| ? 1 : 0;
