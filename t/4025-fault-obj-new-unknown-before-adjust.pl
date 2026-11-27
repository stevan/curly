# kind: fault
# model: t/models/obj.py
use v5.42;
use experimental 'class';
sub noisy() {
say "noisy";
return 1;
}
class S { field $f = main::noisy(); ADJUST { say "adjust" } }
say(1);
S->new(b => 1);
say(2);
