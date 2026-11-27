# kind: fault
# perl's map has the range's values once, too; the exception is the loop's alone, and a map's list is frozen: perl prints 0, 1.
use v5.42;
my @a = (1, 2);
say "start";
my @b = map { push @a, 1; $_ } 0 .. $#a;
