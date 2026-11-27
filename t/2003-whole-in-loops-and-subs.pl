# model: t/models/whole.py
use v5.42;
sub show($v) {
    return "u" unless defined $v;
    return "[" . join(",", map { show($_) } $v->@*) . "]" if ref($v) eq "ARRAY";
    return "{" . join(",", map { $_ . ":" . show($v->{$_}) } sort keys $v->%*) . "}" if ref($v) eq "HASH";
    return $v;
}
sub total(@xs) {
    my $t = 0;
    $t += $_ for @xs;
    return $t;
}
sub items($r) {
    return $r->@*;
}
sub pairs($h) {
    return map { $_ . $h->{$_} } sort keys $h->%*;
}
sub count($r) {
    return scalar(@{$r});
}
sub grow($r, $n) {
    push $r->@*, $n;
    return;
}
sub opts($x, %o) {
    return $x . join(",", map { "$_=$o{$_}" } sort keys %o);
}
{
    my $r = [1, 2, 3];
    my $t = 0;
    for my $x ($r->@*) {
        $t += $x;
    }
    say($t);
    for my $x (@{$r}, 10) {
        print($x, " ");
    }
    say("");
    for my $i (0 .. $r->$#*) {
        say($i, ":", $r->[$i]);
    }
    my $h = {b => [2, 3], a => [1]};
    for my $k (sort keys $h->%*) {
        say($k, "=", join(",", $h->{$k}->@*));
    }
    say(join(",", sort map { scalar($_->@*) } values $h->%*));
    for my $k (sort keys %{$h}) {
        delete $h->{$k};
    }
    say(scalar(%{$h}));
    my $grid = [[1, 2], [3, 4]];
    for my $row ($grid->@*) {
        say(join(" ", map { $_ * 10 } $row->@*));
    }
    my $s = 0;
    $s += $_ for $grid->[1]->@*;
    say($s);
    for ($grid->@*) {
        push $_->@*, 0;
    }
    say(show($grid));
    my $w = [3, 1, 2];
    for my $x ($w->@[2, 0]) {
        say($x);
    }
    my $words = {one => 1, two => 2, three => 3};
    for my $x ($words->@{"two", "one"}) {
        say($x);
    }
}
{
    my $r = [5, 3, 9, 1];
    my $h = {x => 2, y => 1};
    say(join(",", sort { $a <=> $b } $r->@*), "|", join(",", sort { $h->{$a} <=> $h->{$b} } keys $h->%*));
    say(join(",", map { $_ + 1 } @{$r}), "|", join(",", grep { $_ > 3 } $r->@*));
    say(join(",", map { $_ * 2 } sort { $a <=> $b } values $h->%*));
    say(join(",", map { $_ } $r->@[1, 2]));
    my @sorted = sort { $a <=> $b } $r->@*;
    $r->@* = sort { $b <=> $a } $r->@*;
    say("@sorted", "|", join(",", $r->@*));
    my $u = [];
    $u->[0] = 3;
    $u->[3] = 1;
    $u->@* = sort { ($a // 0) <=> ($b // 0) } $u->@*;
    say(join(",", map { $_ // "u" } $u->@*));
}
{
    my $r = [1, 2, 3];
    say(total($r->@*), total(@{$r}, 4), total($r->@[0, 2]));
    my @got = items($r);
    say(scalar(@got), join(",", items([7, 8])), join(",", pairs({b => 2, a => 1})));
    say(count($r), count([]));
    my $e;
    grow($r, 4);
    my $f = [];
    grow($f, 5);
    say(join(",", $r->@*), show($f));
    my $o = {b => 2, a => 1};
    say(opts("o:", $o->%*));
}
