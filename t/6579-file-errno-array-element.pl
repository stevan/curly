# kind: refused
# perl gives an element of @!, and warns.
use v5.42;
say $![0];
