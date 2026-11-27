# kind: fault
# perl dies: Can't use string ("a") as a HASH ref while "strict refs" in use.
use v5.42;
my $r = "a";
undef $r->{k};
