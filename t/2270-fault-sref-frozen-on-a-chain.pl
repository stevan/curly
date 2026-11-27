# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my $x = 1;
my $r = [\$x];
my $s = $r;
for my $v ($r->[0]->$*) {
    push $s->@*, 2;
    last;
}
say(2);
