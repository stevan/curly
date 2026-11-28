use v5.42;
BEGIN {
    my $x = 10;
    *FOO = sub () { $x };
    $x++;
}
print FOO(); # printed 10 prior to 5.32.0
