# kind: refused
# perl runs it: \b in a class is a backspace.
use v5.42;
my $s = "ab";
say $s =~ /[\b]/ ? 1 : 0;
