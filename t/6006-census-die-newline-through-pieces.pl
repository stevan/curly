# a die over two lines whose message ends in a newline through a concatenation or a sprintf: caught, and printed as perl makes it (D261).
use v5.42;
my @l = (1, 2);
try {
    die "cycle among: " . join(" ", @l) . "\n"
        if @l;
}
catch ($e) {
    print "caught: $e";
}
my $n = 3;
try {
    die sprintf("has %d\n", $n)
        if $n;
}
catch ($e) {
    print "caught: $e";
}
try {
    die "a" . ("b" . "\n")
        if $n;
}
catch ($e) {
    print "caught: $e";
}
