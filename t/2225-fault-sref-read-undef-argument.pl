# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
sub f($v) {
    return $v;
}
my $r;
f(${ $r });
say(2);
