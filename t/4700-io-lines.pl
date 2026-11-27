# t/models/io.py 4700
# stdin: bc\n\n \n0\nbc\n\n0
use v5.42;
my $first = <STDIN>;
print "first [$first]";
my $n = 0;
while (my $line = <STDIN>) { $n++; print "$n [$line]"; }
say "";
my $after = <STDIN>;
say defined $after ? "a line" : "undef";
$after = <STDIN>;
say defined $after ? "a line" : "undef";
my @none = <STDIN>;
say scalar(@none);
