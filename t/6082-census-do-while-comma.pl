# kind: refused
# perl runs say for ever: the test is the list, its last value say's (T131).
use v5.42;
my $i = 0;
do {
    $i++;
} while ($i < 3), say "x";
