# kind: refused
# perl runs it: 'a', 'b' (T543).
use v5.42;
my $s = "ab";
while ($s =~ /(\w)/g) {
    last;
}
