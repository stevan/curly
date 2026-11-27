# kind: refused
# perl does not compile it: syntax error near ")[".
use v5.42;
my @x = (1);
my @s = (sort(@x)[0]);
