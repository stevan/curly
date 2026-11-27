# t/models/io.py 4702
# stdin:  \nbc\n0.5\nq\0011z\n
use v5.42;
sub count(@lines) { return scalar(@lines) }
sub last_of(@lines) { return $lines[-1] }
my $first = <STDIN>;
say count(<STDIN>);
say count(<STDIN>);
print "[$first]";
say join("|", "x", <STDIN>, "y");
