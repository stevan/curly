# kind: refused
# perl prints nothing: $x is a file handle to it.
use v5.42;
my $x = 5;
print $x isa Foo;
