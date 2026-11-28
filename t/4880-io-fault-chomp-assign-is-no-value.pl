# kind: fault
# stdin: a\nb\nc\n
# chomp(my $x = EXPR) is worth how many characters chomp took, to perl,
# and nothing here, as chomp($x) is nothing (D130, D219): a sub that ends
# in one has no value (T522). perl prints 1.
use v5.42;
sub line() { chomp(my $l = <STDIN>) }
line();
say "void";
my $v = line();
say $v;
