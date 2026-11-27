# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
sub f() {
    return undef;
}
push f()->@*, 1;
say(2);
