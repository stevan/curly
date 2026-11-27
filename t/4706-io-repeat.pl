# t/models/io.py 4706
# stdin: a\nb\nc\n
use v5.42;
my $twice = <STDIN> x 2;
print $twice;
my @twice = (<STDIN>) x 2;
print @twice;
say scalar(@twice);
