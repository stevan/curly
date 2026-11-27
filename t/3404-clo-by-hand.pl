# Subs with no name and calls through a reference, by hand, with perl's
# answers (step 14): what the model of closures does not write.
use v5.42;
no warnings 'recursion';
# The orders (T370): the arguments, then what stands before the arrow,
# then the call; an argument that is a variable is read when the sub
# copies it, after what stands before the arrow has run.
my $x = 1;
sub mk() {
    $x = 5;
    return sub ($v) { $v };
}
say mk()->($x + 0), mk()->($x);
my $f = sub ($n) { "f$n" };
my $g = sub ($n) { "g$n" };
say $f->(($f = $g) ? 1 : 0);
# A taken scalar and a closure share the variable (13c's cell).
my $s = 1;
my $r = \$s;
my $get = sub { $s };
$r->$* = 2;
say $get->(), ${ $r };
# A closure over a catch's variable, over a slurpy parameter, and over a
# hash parameter.
my @caught;
for my $n (1 .. 2) {
    try {
        die "e$n\n";
    }
    catch ($e) {
        push @caught, sub { $e };
    }
}
say join("", map { $_->() } @caught);
sub rest($first, @more) {
    return sub { $first . scalar(@more) . join("", @more) };
}
say rest(1, 2, 3)->(), rest(4)->();
# `__SUB__` in the block of a map in a sub with no name is that sub (D166).
my $depth = sub ($t) { return ref($t) ? 1 + (sort { $b <=> $a } map { __SUB__->($_) } $t->@*)[0] : 0 };
say $depth->([1, [2, [3]], [4]]);
# `\&name` before the sub is written, and one value for the whole run.
my $later = \&later;
sub later($v) {
    return "later$v";
}
say $later->(1), $later == \&later ? " same" : " diff";
# An array among the arguments of a call through a reference flattens.
my @args = (2, 3);
my $sum = sub (@l) { my $t = 0; $t += $_ for @l; return $t };
say $sum->(1, @args, 4), $sum->(), $sum->(@args);
# A sub that gives a list hands it on through a call through a reference.
my $pair = sub { return (7, 8) };
my %d = (p => $pair);
my @got = ($d{p}(), $d{p}->());
say "@got ", scalar(@got);
# `last` and `next` inside a sub with no name, to a loop in it.
my $firsts = sub (@l) {
    my @out;
    for my $v (@l) {
        next if $v < 0;
        last if $v > 9;
        push @out, $v;
    }
    return join(",", @out);
};
say $firsts->(1, -2, 3, 10, 4);
# A closure made in a loop over a range takes its own value each time
# round, whatever the loop holds later.
my @c;
for my $i (1 .. 3) {
    push @c, sub { $i };
}
say join("", map { $_->() } @c);
# Recursion a thousand deep through a reference.
my $down;
$down = sub ($n) { return $n == 0 ? 0 : 1 + $down->($n - 1) };
say $down->(1000);
# Two subs with no name that use each other, through file variables.
my ($even, $odd);
$even = sub ($n) { return $n == 0 ? "even" : $odd->($n - 1) };
$odd = sub ($n) { return $n == 0 ? "odd" : $even->($n - 1) };
say $even->(7), $odd->(7);
# The value of a sub with no name's last statement, and `true` after a say.
my $last = sub ($v) { $v * 2 };
my $said = sub { say "said" };
say $last->(21), " ", $said->() ? "true" : "false";
# A sub with no name in a string is D112's: not here. In a ternary, as a
# default, as an argument.
my $pick = 1 ? sub { "one" } : sub { "two" };
say $pick->(), (sub ($h = sub { "dflt" }) { $h->() })->(), (sub ($k) { $k->() })->(sub { "arg" });
