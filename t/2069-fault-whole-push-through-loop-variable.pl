# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my @l = (undef);
for my $x (@l) {
    push $x->@*, 1;
}
say(2);
