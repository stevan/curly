use v5.42;
sub foo ($name //= "world") {
    print "Hello, $name";
}

foo(undef);  # will print "Hello, world"
