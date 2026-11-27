# model: t/models/whole.py
use v5.42;
sub show($v) {
    return "u" unless defined $v;
    return "[" . join(",", map { show($_) } $v->@*) . "]" if ref($v) eq "ARRAY";
    return "{" . join(",", map { $_ . ":" . show($v->{$_}) } sort keys $v->%*) . "}" if ref($v) eq "HASH";
    return $v;
}
{
    my $r;
    $r->@* = (1, 2, 3);
    say(show($r));
    @{$r} = ($r->@*, 4);
    say(show($r));
    $r->@* = reverse $r->@*;
    say(show($r));
    @{$r} = ();
    say(show($r));
    my $h;
    $h->%* = (a => 1, b => [2]);
    %{$h->{inner}} = (c => 3, c => 4);
    $h->{list}->@* = (5);
    say(show($h));
    $h->%* = ();
    say(show($h));
    my @a = (1, 2);
    my $ra = \@a;
    $ra->@* = (7, 8, 9);
    my %g = (k => 1);
    my $rg = \%g;
    %{$rg} = (j => 2);
    say("@a", join(",", map { "$_$g{$_}" } sort keys %g));
    my $x;
    my $s = [0];
    ($x, $s->@*) = (1, 2, 3);
    my $t;
    ($t->@*) = (4, 5);
    my $y;
    my $u = {};
    ($y, %{$u}) = ("p", a => 1);
    say($x, show($s), show($t), $y, show($u));
}
{
    my $r;
    $r->@[0, 2] = ("a", "c");
    say(show($r));
    $r->@[1, 4] = ("b");
    say(show($r));
    $r->@[-1, -5] = (5, 1);
    say(show($r));
    my $h;
    $h->@{"x", "y"} = (1, 2);
    $h->{in}->@{"p", "q"} = (3);
    $h->{l}->@[1] = (4);
    say(show($h));
    my @parts = $h->@{"y", "x"};
    say(join(",", @parts));
}
