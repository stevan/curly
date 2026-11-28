use v5.42;
BEGIN {
    my $x = 10;
    *FOO = sub () { return $x };
    $x++;
}
print FOO(); # prints 11
