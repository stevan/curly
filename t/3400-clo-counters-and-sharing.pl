# model: t/models/clo.py
use v5.42;
sub counter($start) {
    my $n = $start;
    return sub { return $n++ };
}
sub later($x, $f = sub { $x }) {
    $x = $x * 10;
    return $f->();
}
my $total = 0;
sub adder() {
    return sub ($n) { $total += $n; return $total };
}
{
    my $c = counter(1);
    my $d = counter(10);
    say(join(",", $c->(), $c->(), $d->(), $c->(), $d->()));
}
{
    my $x = 1;
    my $get = sub { $x };
    my $set = sub ($v) { $x = $v; return };
    say($get->());
    $set->(5);
    say($get->(), $x);
    $x = 7;
    say($get->());
    $x .= "a";
    say($get->());
    my @a = (1);
    my %h = (k => "v");
    my $push = sub ($e) { push @a, $e; return scalar(@a) };
    my $put = sub ($k, $v) { $h{$k} = $v; return };
    say($push->(2));
    $push->(3);
    $put->("j", "w");
    say("@a ", join(",", map { "$_=$h{$_}" } sort keys %h));
    @a = (9);
    say($push->(8), " @a");
}
{
    my $add = sub ($x) { return sub ($y) { return sub ($z) { $x + $y + $z } } };
    say($add->(1)->(2)->(3), $add->(10)(20)(30));
    my $mk = sub ($base) { my $count = 0; return sub ($inc) { $count += $inc; return $base . ":" . $count } };
    my $p = $mk->("p");
    my $q = $mk->("q");
    say(join(",", $p->(1), $p->(2), $q->(5), $p->(3)));
    say(later(4), later(5, sub { "given" }));
    my $any = sub { "any" };
    say($any->(), $any->(1, 2, 3));
}
{
    my $a1 = adder();
    my $a2 = adder();
    $a1->(5);
    $a2->(6);
    say($total, " ", $a1 == $a2 ? "same" : "diff");
}
