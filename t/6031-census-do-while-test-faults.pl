# kind: fault
# perl warns: Use of uninitialized value $n in numeric lt (<), and runs once: '1'. The fault names the line of the do.
use v5.42;
my $n;
my $i = 0;
do {
    $i++;
    say $i;
} while ($i < $n);
