# kind: refused
# perl compiles it; a call P->new calls the sub, and dies (T407): Can't locate object method "new" via package "sub".
use v5.42;
use experimental 'class';
sub P() {
    return "sub";
}
class P { }
