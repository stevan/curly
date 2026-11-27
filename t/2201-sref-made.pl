# model: t/models/sref.py
use v5.42;
sub show($v) {
    return "u" unless defined $v;
    return "\\" . show($v->$*) if ref($v) eq "SCALAR" || ref($v) eq "REF";
    return "[" . join(",", map { show($_) } $v->@*) . "]" if ref($v) eq "ARRAY";
    return "{" . join(",", map { $_ . ":" . show($v->{$_}) } sort keys $v->%*) . "}" if ref($v) eq "HASH";
    return $v;
}
sub set($r, $v) {
    $r->$* = $v;
    return $r;
}
{
    my $r;
    $r->$* = 5;
    say(ref($r), " ", ${ $r });
    my $s1;
    ${ $s1 } += 2;
    say(ref($s1), " ", show($s1));
    my $s3;
    ${ $s3 } -= 3;
    say(ref($s3), " ", show($s3));
    my $s5;
    ${ $s5 } .= "x";
    say(ref($s5), " ", show($s5));
    my $s7;
    ${ $s7 } //= 4;
    say(ref($s7), " ", show($s7));
    my $s9;
    ${ $s9 } ||= "y";
    say(ref($s9), " ", show($s9));
    my $s11;
    ${ $s11 } &&= 9;
    say(ref($s11), " ", show($s11));
    my $i;
    $i->$*++;
    my $j;
    --${ $j };
    my $k;
    my $old = ${ $k }++;
    say(${ $i }, $j->$*, $k->$*, $old);
    my $e;
    my $f;
    (${ $e }, $f->$*) = (1, 2);
    say(show($e), show($f));
}
{
    my @a;
    $a[1]->$* = 3;
    ${ $a[3] } .= "x";
    say(show(\@a));
    my %h;
    $h{k}->$* = 4;
    ${ $h{j} } += 2;
    $h{i}->$*++;
    say(show(\%h));
    my $t;
    $t->{a}[1]->$* = 6;
    ${ $t->{b} } //= 7;
    ${ $t->{c}{d} } = 8;
    say(show($t));
    my $z = 0;
    my $l = [undef, \$z];
    $l->[0]->$* = 1;
    $l->[1]->$* = 2;
    ${ $l->[2] } = 3;
    say(show($l), $z);
    my $was = $l->[1];
    ${ $l->[1] } += 10;
    say($was == $l->[1] ? "same" : "made", " ", $was->$*);
}
{
    my $p = set(undef, 1);
    my $q;
    my $back = set($q, 2);
    say(show($p), " ", defined($q) ? "made" : "u", " ", show($back));
    my $x = 0;
    set(\$x, 9);
    say($x);
}
{
    my $r;
    ${ $r } = $r;
    say(ref($r), " ", $r == $r->$* ? "cycle" : "no", " ", ref(${ ${ $r } }));
    my $x;
    my $y = \$x;
    $x = $y;
    say(ref($y), " ", ref($x), " ", $x == $y ? "same" : "diff");
}
