# kind: refused
# perl prints 1 on stderr.
use v5.42;
my $f = "%d\n";
printf STDERR $f, 1;
