# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $h = {a => 1};
my $g = $h;
for my $v ($h->@{"a"}) {
    delete $g->@{"a"};
    last;
}
say(2);
