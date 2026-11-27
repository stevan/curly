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
    push $r->@*, 1, 2;
    say(show($r));
    unshift @{$r}, 0;
    say(show($r));
    my $h;
    push $h->{list}->@*, "a";
    push @{$h->{list}}, "b";
    push $h->{deep}[2]{more}->@*, 3;
    unshift $h->{deep}[0]->@*, 4, 5;
    say(show($h));
    my $s;
    splice($s->@*, 0, 0, 7, 8);
    splice(@{$s->[5]}, 0, 0, 9);
    say(show($s));
}
{
    my $r = [1, 2, 3, 4, 5];
    my @gone = splice($r->@*, 1, 2);
    say(join(",", @gone));
    say(show($r));
    my @also = splice(@{$r}, 1, 1, "x", "y");
    say(join(",", @also));
    splice($r->@*, 3);
    say(show($r));
    splice(@{$r}, -1, 1);
    say(show($r));
    my $v0 = pop $r->@*;
    say(defined($v0) ? $v0 : "u");
    my $v1 = shift @{$r};
    say(defined($v1) ? $v1 : "u");
    my $v2 = pop $r->@*;
    say(defined($v2) ? $v2 : "u");
    say(show($r));
    my $t = {a => [1], b => {c => [2, 3]}};
    push $t->{a}->@*, 4;
    my $last = pop $t->{b}{c}->@*;
    unshift @{$t->{b}->{c}}, $last;
    push $t->{new}->@*, scalar($t->{a}->@*);
    say(show($t));
    my @a = ([1]);
    my %h;
    push $a[0]->@*, 2;
    push $a[2]->@*, 3;
    push @{$h{k}}, 4;
    push $h{k}->@*, 5;
    say(show(\@a), show(\%h));
    my $c = [1, 2];
    push $c->@*, $c->@*;
    unshift $c->@*, scalar($c->@*);
    say(show($c));
}
{
    my $h = {a => 1, b => 2, c => 3, d => [4]};
    my @d = delete $h->@{"a", "c", "nope"};
    say(join(",", map { show($_) } @d));
    say(show($h));
    delete $h->@{"b"};
    say(show($h));
    my $n = {x => {p => 1, q => 2}};
    my @e = delete $n->{x}->@{"q"};
    say(join(",", @e));
    say(show($n));
}
