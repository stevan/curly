# kind: refused
# perl closes the handle in the element; here there is none, and it dies.
use v5.42;
my %h;
close $h{fh};
