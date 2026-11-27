# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
sub g() {
    return undef;
}
${ g() } = 5;
say(2);
