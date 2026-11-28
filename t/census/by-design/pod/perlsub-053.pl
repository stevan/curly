use v5.42;
my ($arg, $n);
$arg = "fred";          # "global" variable
$n = cube_root(27);
print "$arg thinks the root is $n\n";
# outputs: fred thinks the root is 3

sub cube_root {
    my $arg = shift;  # name doesn't matter
    $arg **= 1/3;
    return $arg;
}
