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
{
    my $x = 5;
    my $r = \$x;
    say(ref($r), " ", show($r->$*), " ", show(${ $r }));
    $r->$* += 3;
    say(show($x));
    ${ $r } -= 1;
    say(show($x));
    $r->$* *= 4;
    say(show($x));
    ${ $r } %= 5;
    say(show($x));
    $r->$* **= 3;
    say(show($x));
    ${ $r } .= "z";
    say(show($x));
    $r->$* x= 2;
    say(show($x));
    $x = 7;
    say(${ $r });
    $r->$* = "s";
    say($x, ref($r));
}
{
    my $x = "ab";
    my $r = \$x;
    say(ref($r), " ", show(${ $r }), " ", show($r->$*));
    ${ $r } .= "c";
    say(show($x));
    $r->$* x= 3;
    say(show($x));
    ${ $r } ||= "no";
    say(show($x));
    $r->$* &&= "yes";
    say(show($x));
    ${ $r } //= "no";
    say(show($x));
    $x = 7;
    say($r->$*);
    ${ $r } = "s";
    say($x, ref($r));
}
{
    my $x = 0;
    my $r = \$x;
    say(ref($r), " ", show($r->$*), " ", show(${ $r }));
    $r->$* ||= 4;
    say(show($x));
    ${ $r } &&= 0;
    say(show($x));
    $r->$* &&= 9;
    say(show($x));
    ${ $r } //= 6;
    say(show($x));
    $r->$* += 2;
    say(show($x));
    $x = 7;
    say(${ $r });
    $r->$* = "s";
    say($x, ref($r));
}
{
    my $x = undef;
    my $r = \$x;
    say(ref($r), " ", show(${ $r }), " ", show($r->$*));
    ${ $r } //= 3;
    say(show($x));
    $r->$* .= "x";
    say(show($x));
    $x = 7;
    say(${ $r });
    $r->$* = "s";
    say($x, ref($r));
}
{
    my $x = undef;
    my $r = \$x;
    say(ref($r), " ", show(${ $r }), " ", show($r->$*));
    ${ $r } += 2;
    say(show($x));
    $r->$* -= 5;
    say(show($x));
    $x = 7;
    say(${ $r });
    $r->$* = "s";
    say($x, ref($r));
}
{
    my $x = 5;
    my $r = \$x;
    my $v42 = ${ $r }++;
    say($v42, " ", $x);
    my $v43 = ++$r->$*;
    say($v43, " ", $x);
    my $v44 = ${ $r }--;
    say($v44, " ", $x);
    my $v45 = --$r->$*;
    say($v45, " ", $x);
    my $u;
    my $s = \$u;
    $s->$*++;
    say($u);
    my $w;
    my $t = \$w;
    --${ $t };
    say($w);
}
{
    my $x = 1;
    my $y = 1;
    my $r = \$x;
    my $s = \$x;
    my $t = \$y;
    say($r == $s ? "same" : "diff", " ", $r != $t ? "diff" : "same", " ", \$x == $r ? "same" : "diff");
    my @a = (1);
    my $ra = \@a;
    say($r == $ra ? "same" : "diff", " ", $r == [1] ? "same" : "diff");
    $s->$* = 3;
    say($x, ${ $r });
}
{
    my $x = 1;
    my $y = 2;
    my $r = \$x;
    my $q = \$r;
    say(ref($q), " ", ref($q->$*), " ", ${ ${ $q } }, " ", ${ $q->$* });
    say(show($q));
    $x = [1, 2];
    say(ref($r), " ", ref(${ $r }), " ", show($r));
    $x = {k => 3};
    say(ref($r), " ", ref($r->$*), " ", show($r));
    $x = \$y;
    say(ref($r), " ", ref(${ $r }), " ", show($r));
    ${ $x } = 5;
    say($y);
    my $u;
    my $ru = \$u;
    say(ref($ru), " ", defined($ru->$*) ? "d" : "u", " ", ref(\$u), " ", ref(\$ru), " ", ref(5), "|", ref(undef), "|");
    my $z = \$x;
    $x = 0;
    say($z ? "true" : "false", " ", defined($z) ? "d" : "u", " ", ${ $z } ? "true" : "false", " ", !$z ? "t" : "f");
}
{
    my $x = 4;
    my @a = (\$x);
    my %h = (k => \$x);
    my $d = {l => [\$x]};
    say(${ $a[0] }, $a[0]->$*, ${ $h{k} }, $h{k}->$*, ${ $d->{l}[0] }, $d->{l}->[0]->$*);
    say(cell(6)->$*, ${ cell(7) }, ${ \$x }, (\$x)->$*);
    ${ $a[0] } += 1;
    $h{k}->$* *= 2;
    ${ $d->{l}[0] } .= "!";
    ${ \$x } .= "?";
    say($x);
    my $c = 1;
    my $y = 0;
    ${ $c ? \$x : \$y } = "w";
    say($x, $y);
}
