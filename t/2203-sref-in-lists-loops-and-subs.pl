# model: t/models/sref.py
use v5.42;
sub show($v) {
    return "u" unless defined $v;
    return "\\" . show($v->$*) if ref($v) eq "SCALAR" || ref($v) eq "REF";
    return "[" . join(",", map { show($_) } $v->@*) . "]" if ref($v) eq "ARRAY";
    return "{" . join(",", map { $_ . ":" . show($v->{$_}) } sort keys $v->%*) . "}" if ref($v) eq "HASH";
    return $v;
}
sub add($p, $q) {
    return $p + $q;
}
sub bump($c) {
    $c->$* += 10;
    return;
}
sub where($c, $p, $q) {
    return $c ? $p : $q;
}
{
    my $x = 1;
    my $y = 2;
    my $r = \$x;
    my $s = \$y;
    say(join(",", $r->$*, ${ $s }, $x + $y, $r->$* + ${ $s }, $s->$* . $r->$*));
    my @l = ($r->$*, $s->$*, $r->$*);
    say("@l");
    for my $v ($r->$*, ${ $s }) {
        say($v * 10);
    }
    say(join(",", map { $_ * 2 } $r->$*, $s->$*), " ", join(",", grep { $_ > 1 } ${ $r }, ${ $s }));
    say(join(",", sort { $b <=> $a } ${ $r }, ${ $s }, 3));
    (${ $r }, $s->$*) = ($s->$*, $r->$*);
    say($x, $y);
    my @refs = (\$x, \$y);
    $_->$* *= 2 for @refs;
    say($x, $y);
    for my $c (@refs) {
        ${ $c } += 1;
    }
    say($x, $y);
    my @v = map { $_->$* } @refs;
    my @g = grep { ${ $_ } > 4 } @refs;
    say("@v ", scalar(@g), " ", ${ $g[0] });
}
{
    my ($cx, $cy) = (1, 2);
    my $x = 1;
    my $r = \$x;
    say(add($r->$*, ${ $r }));
    bump($r);
    bump(\$x);
    say($x);
    ${ where(1, \$cx, \$cy) } = 10;
    where(0, \$cx, \$cy)->$* .= "y";
    say($cx, $cy);
    my %h = (a => \$x);
    ${ $h{a} } = 0;
    say($x);
}
{
    my $x = 1;
    try {
        die \$x;
    }
    catch ($e) {
        say(ref($e), " ", $e->$*, " ", $e == \$x ? "same" : "diff");
    }
}
