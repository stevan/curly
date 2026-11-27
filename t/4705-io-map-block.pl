# t/models/io.py 4705
# stdin: 0.5\n\n0.5\n
use v5.42;
my @all = map { <STDIN> } 1 .. 3;
say scalar(@all);
my @tested = grep { defined(<STDIN>) } 1 .. 2;
say scalar(@tested);
print @all;
