# model: t/models/clo.py
use v5.42;
sub twice($f, $v) {
    return $f->($f->($v));
}
sub inc($n) {
    return $n + 1;
}
my $g = 1;
sub plain() {
    return sub { 1 };
}
sub uses() {
    return sub { $g };
}
my @log;
sub arg($v) {
    push @log, "arg$v";
    return $v;
}
sub fn($w) {
    push @log, "fn$w";
    return sub ($v) { push @log, "call$v"; return $v };
}
{
    my %d = (add => sub ($x, $y) { $x + $y }, mul => sub ($x, $y) { $x * $y }, neg => sub ($x) { -$x });
    my @fs = (sub { "zero" }, sub ($v) { "one:$v" });
    say($d{add}->(2, 3), " ", $d{mul}(4, 5), " ", $d{neg}->(6), " ", $fs[0](), " ", $fs[1]->("x"));
    my $t = {ops => [sub ($n) { $n + 1 }, sub ($n) { $n * 2 }]};
    say($t->{ops}[0]->(5), $t->{ops}->[1](5), $t->{ops}[1](5));
    my $mk = sub { return [sub { "in" }] };
    say($mk->()[0]->(), $mk->()->[0](), sub { 3 }->());
}
{
    my $r = \&inc;
    say(twice($r, 1), twice(\&inc, 5), " ", ref($r), " ", $r == \&inc ? "same" : "diff", " ", (\&inc)->(9));
    say(twice(sub ($x) { $x . "!" }, "a"));
}
{
    my @c;
    my @o;
    for my $i (1 .. 2) {
        push @c, sub { 2 };
        push @o, sub { $i };
    }
    say($c[0] == $c[1] ? "same" : "diff", $o[0] == $o[1] ? "same" : "diff", plain() == plain() ? "same" : "diff", uses() == uses() ? "same" : "diff");
    my $f = sub { 1 };
    my $h = $f;
    say($f == $h ? "same" : "diff", $f != sub { 5 } ? "diff" : "same", $f ? "true" : "false", defined($f) ? "d" : "u", ref(sub { }), "|", ref(\$f));
}
{
    my $fact = sub ($n) { return $n <= 1 ? 1 : $n * __SUB__->($n - 1) };
    say($fact->(10));
    my $fib;
    $fib = sub ($n) { return $n < 2 ? $n : $fib->($n - 1) + $fib->($n - 2) };
    say($fib->(15));
    my $walk = sub ($t) { return ref($t) ? join("", map { __SUB__->($_) } $t->@*) : $t };
    say($walk->([1, [2, [3, 4]], 5]));
}
{
    my $list = sub { return (1, 2, 3) };
    my $one = sub { return 7 };
    my @l = $list->();
    my ($first) = $list->();
    say(scalar(@l), $first, " ", $one->() + 1, " ", join(",", $list->(), $one->()));
    my $none = sub { return };
    my @n = ($none->(), 1);
    my $u = $none->();
    say(scalar(@n), defined($u) ? "d" : "u");
    my $sl = sub ($x, @rest) { return scalar(@rest) . $x };
    my $hs = sub (%o) { return join(",", map { "$_$o{$_}" } sort keys %o) };
    say($sl->(1, 2, 3), " ", $hs->(b => 2, a => 1), " ", $sl->(@l));
    my $dflt = sub ($x, $y = 5, $z //= 6) { return "$x$y$z" };
    say($dflt->(1), $dflt->(1, 2), $dflt->(1, 2, undef), $dflt->(1, 2, 3));
}
{
    fn(1)->(arg(2));
    my $i = 0;
    my @fs = (sub { "zero" }, sub { "one" });
    say("@log ", $fs[$i]->($i = 1));
    my $total = 5;
    my $step = sub { $total += 100; return 1 };
    say($total + $step->());
}
