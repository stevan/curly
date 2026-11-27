# kind: refused
# perl warns: Useless use of a constant in void context; it matches the last.
use v5.42;
my $r = ("a", "b") =~ /b/;
