# kind: refused
# perl warns: sort (...) interpreted as function (T190).
use v5.42;
my @a = (2, 1);
my @s = (sort (@a), 9);
