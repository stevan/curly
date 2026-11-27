# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
sub none() {
    return undef;
}
none()->();
say(2);
