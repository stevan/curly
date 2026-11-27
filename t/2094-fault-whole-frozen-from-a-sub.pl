# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [1, 2];
sub grow($s) {
    push $s->@*, 3;
    return;
}
for my $x ($r->@*) {
    grow($r);
    last;
}
say(2);
