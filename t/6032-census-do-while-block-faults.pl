# kind: fault
# perl warns: Use of uninitialized value in addition, twice, and ends: '1', '2'.
use v5.42;
my $i = 0;
my $u;
do {
    $i++;
    say $i;
    say $i + $u if $i == 2;
} while ($i < 2);
