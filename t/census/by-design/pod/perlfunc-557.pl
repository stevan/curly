use v5.42;
my $x = '1234';
for (substr($x, -3, 2)) {
    $_ = 'a';   print $x,"\n";    # prints 1a4, as above
    $x = 'abcdefg';
    print $_,"\n";                # prints f
}
