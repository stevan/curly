# a statement joined to a die, a return, a last or a next by or and and: perl's meaning, the second run when the first's value says so (D260).
use v5.42;
my %ops = (a => 1, b => 0);
my $f = $ops{a} or die "no a\n";
say $f;
sub get($k) {
    my $v = $ops{$k} or return "none";
    return "got $v";
}
say get("a"), " ", get("b"), " ", get("c");
for my $i (1 .. 4) {
    my $v = $i % 2 or next;
    $i < 3 or last;
    say "odd $i $v";
}
my $n = 0;
OUT: for my $i (1 .. 3) {
    for my $j (1 .. 3) {
        $n++;
        $j == 2 and next OUT;
    }
}
say $n;
my @l = (1);
scalar(@l) or die "empty\n";
$ops{b} and die "b is true\n";
my $g = $ops{b} || "default" or die "never\n";
say $g;
sub check($x) {
    $x > 0 or return;
    return $x;
}
say check(3);
