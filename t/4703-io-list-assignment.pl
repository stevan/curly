# t/models/io.py 4703
# stdin: -1\n \n-1\n0.5\n
use v5.42;
my ($p, $q) = <STDIN>;
my $r = <STDIN>;
print "[$p][$q]";
say defined $r ? "more" : "none";
my %h = (a => 1);
my @got = (<STDIN>);
say scalar(@got);
