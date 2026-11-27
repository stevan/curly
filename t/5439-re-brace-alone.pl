# kind: refused
# perl warns: Unescaped left brace in regex is passed through (T542).
use v5.42;
my $s = "ab";
say $s =~ /a{b/ ? 1 : 0;
