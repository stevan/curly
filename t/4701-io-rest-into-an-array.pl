# t/models/io.py 4701
# stdin:  \n\n42\n42\n 
use v5.42;
my $one = <STDIN>;
my @rest = <STDIN>;
say scalar(@rest);
print "[$one]";
print "<$_>" for @rest;
say "";
say $#rest;
