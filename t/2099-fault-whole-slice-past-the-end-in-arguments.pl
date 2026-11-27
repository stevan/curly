# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [1];
sub f(@x) {
    return;
}
f($r->@[0, 1]);
say(2);
