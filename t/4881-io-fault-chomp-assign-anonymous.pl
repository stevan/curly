# kind: fault
# stdin: a\nb\n
# The same of a sub with no name, and of the assignment to a variable
# declared before (T522). perl prints 1.
use v5.42;
my $x;
my $f = sub { chomp($x = <STDIN>) };
$f->();
say "[$x]";
my @l = ($f->());
say scalar(@l);
