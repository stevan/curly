# A die through calls through references, caught (step 14; D141): the
# frames, the freezes and the sorts each call had open are given back, so
# the array a loop in a closure was over may be changed after the catch.
use v5.42;
no warnings 'recursion';
my @a = (1, 2, 3);
my $walk = sub ($stop) {
    for my $x (@a) {
        die "stop at $x\n" if $x == $stop;
    }
    return "walked";
};
try {
    $walk->(2);
}
catch ($e) {
    print "caught: $e";
}
push @a, 4;
say "@a ", $walk->(9);
my $deep;
$deep = sub ($n) {
    die "bottom\n" if $n == 0;
    my @s = sort { $a <=> $b } (3, 1, 2);
    return $deep->($n - 1) . $s[0];
};
for my $round (1 .. 3) {
    try {
        $deep->(500);
    }
    catch ($e) {
        chomp $e;
        say "$round: $e";
    }
}
my %d = (boom => sub { die { code => 7 } });
try {
    $d{boom}->();
}
catch ($e) {
    say "code ", $e->{code};
}
