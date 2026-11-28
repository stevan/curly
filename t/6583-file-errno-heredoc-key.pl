# kind: refused
# perl gives an element of %!.
use v5.42;
print <<"END";
why: $!{x}
END
