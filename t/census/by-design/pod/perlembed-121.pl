use v5.42;
#test.pl
my $string = "hello";
foo($string);

sub foo {
    print "foo says: @_\n";
}
