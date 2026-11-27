# t/models/io.py 4704
# stdin:  \nbc\n42\n0\na
use v5.42;
my $n = 0;
for my $line (<STDIN>) { $n++; print "$n<$line>"; }
say "";
say "done $n";
