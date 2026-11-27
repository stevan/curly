use v5.42;
use experimental 'class';
class P {
    field $y :param
        = die "no y";
}
P->new;
