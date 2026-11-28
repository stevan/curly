# kind: refused
# perl runs it: '3'.
use v5.42;
my $i = 0;
do {
    $i++;
} while (my $z = $i < 3);
