# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my @a = (1, 2);
my $r = \@a;
for my $x (@a) {
    push $r->@*, 3;
    last;
}
say(2);
