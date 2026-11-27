# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [1, 2];
my $s = $r;
for my $x ($r->@*) {
    unshift $s->@*, 0;
    last;
}
say(2);
