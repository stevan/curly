# model: t/models/sref.py
use v5.42;
sub show($v) {
    return "u" unless defined $v;
    return "\\" . show($v->$*) if ref($v) eq "SCALAR" || ref($v) eq "REF";
    return "[" . join(",", map { show($_) } $v->@*) . "]" if ref($v) eq "ARRAY";
    return "{" . join(",", map { $_ . ":" . show($v->{$_}) } sort keys $v->%*) . "}" if ref($v) eq "HASH";
    return $v;
}
sub cell($v) {
    my $c = $v;
    return \$c;
}
sub param($v) {
    my $r = \$v;
    $r->$* += 1;
    return $v;
}
sub keep($v, $w = 3) {
    return (\$v, \$w);
}
{
    my @r;
    for my $i (1 .. 3) {
        my $v = $i * 10;
        push @r, \$v;
    }
    say(join(",", map { $_->$* } @r));
    ${ $r[0] } = 5;
    say(join(",", map { ${ $_ } } @r), " ", $r[0] == $r[1] ? "same" : "diff");
    my @w;
    my $n = 0;
    while ($n < 3) {
        my $c = $n++;
        push @w, \$c;
    }
    say(join(",", map { $_->$* } @w));
    my @q = (1, 2, 3);
    my @t;
    while (my $e = shift @q) {
        push @t, \$e;
    }
    say(join(",", map { $_->$* } @t));
    my @c;
    for (my $i = 0; $i < 3; $i++) {
        push @c, \$i;
    }
    say(join(",", map { $_->$* } @c));
    my @o;
    my $one;
    for my $i (1 .. 2) {
        $one = $i;
        push @o, \$one;
    }
    say(join(",", map { $_->$* } @o), " ", $o[0] == $o[1] ? "same" : "diff");
    my @m = map { my $v = $_; \$v } (4, 5);
    say(join(",", map { $_->$* } @m));
}
{
    my $p = cell(1);
    my $q = cell(2);
    say($p->$*, $q->$*, " ", $p == $q ? "same" : "diff");
    my $x = 1;
    say(param($x), " ", $x);
    my ($k1, $k2) = keep(5);
    ${ $k1 } .= "a";
    $k2->$* .= "b";
    say($k1->$*, ${ $k2 });
}
my $early = early();
$early->$* = 7;
my $late;
sub early() {
    return \$late;
}
say($late, " ", ${ early() }, " ", early() == $early ? "same" : "diff");
{
    my @r;
    for my $n (1 .. 2) {
        try {
            die "e$n\n";
        }
        catch ($e) {
            push @r, \$e;
        }
    }
    say(join("", map { $_->$* } @r));
    my ($x, $y) = (1, 2);
    my $r = \$x;
    ($x, $y) = ($y, $x);
    say("$x $y ", $r->$*);
}
