# kind: refused
# perl gives 1, the characters chomp took (T522).
use v5.42;
my @l = map { chomp(my $x = $_) } "a\n";
