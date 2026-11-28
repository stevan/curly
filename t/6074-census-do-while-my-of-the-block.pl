# kind: refused
# perl does not compile it: Global symbol "$j" requires explicit package name.
use v5.42;
my $i = 0;
do {
    my $j = $i;
    $i++;
} while ($j < 3);
