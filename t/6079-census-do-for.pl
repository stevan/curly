# kind: refused
# perl runs it three times.
use v5.42;
my $i = 0;
do {
    $i++;
} for 1 .. 3;
