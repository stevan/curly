# t/models/io.py 4719
# stdin: \nbc\nbc\nq\0011z\n
use v5.42;
sub first_line() { my $l = <STDIN>; return $l }
sub the_rest() { return <STDIN> }
sub also_the_rest() { <STDIN> }
my $one = first_line();
my @rest = the_rest();
my @none = also_the_rest();
print "[$one]";
say scalar(@rest), " ", scalar(@none);
