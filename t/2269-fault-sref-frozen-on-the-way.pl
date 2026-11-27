# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my %h = (b => 2);
my $x = 1;
$h{a} = \$x;
my $g = \%h;
for my $v ($h{a}->$*) {
    $g->{c} = 3;
    last;
}
say(2);
