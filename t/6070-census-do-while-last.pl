# kind: refused
# perl dies: Can't "last" outside a loop block.
use v5.42;
my $i = 0;
do {
    $i++;
    last if $i == 2;
} while ($i < 5);
