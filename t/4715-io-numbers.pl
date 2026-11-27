# t/models/io.py 4715
# stdin: -37\n40\n-17\n38\n-14\n15\n
use v5.42;
my $total = 0;
my $count = 0;
while (my $line = <STDIN>) { $total += $line; $count++; }
say "$count numbers, total $total";
