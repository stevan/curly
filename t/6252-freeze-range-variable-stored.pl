# kind: refused
# perl changes its own copy: 2, 3.
use v5.42;
my $n = 2;
for my $i (1 .. $n) {
    $i++;
}
