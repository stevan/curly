# kind: refused
# perl runs it, and says nothing: a reference to the list's own element.
use v5.42;
my @l = (1, 2);
my @r;
for (@l) {
    push @r, \$_;
}
