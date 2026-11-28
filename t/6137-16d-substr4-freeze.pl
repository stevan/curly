# kind: fault
# perl changes the element the loop is over: 'ab', then 'xb'.
use v5.42;
my @a = ("ab", "cd");
for my $e (@a) {
    say $e;
    my $s = $e;
    substr($s, 0, 1, "x");
    @a = ($s);
}
