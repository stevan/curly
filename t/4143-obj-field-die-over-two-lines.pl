# kind: refused
# perl names the field's first line (T436): no y at FILE line 5.
use v5.42;
use experimental 'class';
class P {
    field $y :param
        = die "no y";
}
