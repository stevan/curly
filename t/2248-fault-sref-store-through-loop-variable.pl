# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my @l = (undef);
for my $x (@l) {
    $x->$* = 1;
}
say(2);
