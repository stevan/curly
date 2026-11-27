# kind: refused
# perl makes the list's element undef.
use v5.42;
my @a = (1, 2);
for (@a) {
    undef $_;
}
