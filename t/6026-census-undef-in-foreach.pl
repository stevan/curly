# kind: fault
# perl makes the list's element undef while the loop is over it: '1', then an empty line and a warning (the loop walks the array itself).
use v5.42;
my @a = (1, 2);
for my $x (@a) {
    say $x;
    undef $a[1];
}
