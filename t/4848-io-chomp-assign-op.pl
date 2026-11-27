# kind: refused
# perl chomps $x.
use v5.42;
my $x = "a";
chomp($x .= "\n");
