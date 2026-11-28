# kind: refused
# perl prints whether $x is a Foo, the empty string: isa is an operator there, and $x no handle. (isa is step 17a's.)
use v5.42;
my $x = 5;
print $x isa Foo;
