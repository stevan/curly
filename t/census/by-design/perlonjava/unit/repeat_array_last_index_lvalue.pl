use v5.42;

my @values;
$#values = 7;
for (($#values) x 2) {
    $_ *= 2;
}

say $#values;

