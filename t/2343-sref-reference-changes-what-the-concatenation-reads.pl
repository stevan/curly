# kind: refused
# perl runs it, and says nothing: $x is 0v (T348).
use v5.42;
my $x;
my @a = (\$x);
my $i = 5;
${ $a[$i = 0] } = $i . "v";
