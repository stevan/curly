# kind: refused
# perl changes the list's elements: 'Zbc Zef'.
use v5.42;
my @a = ("abc", "def");
for my $x (@a) {
    substr($x, 0, 1, "Z");
}
