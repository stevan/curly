# kind: fault
# A fault after a method call names the line of the statement it is in,
# not the method's own last line (D34): the line is stored again after
# every call. The breakages of the step showed no test reached it.
use v5.42;
use experimental 'class';
class P {
    method m {
        my $x = 1;
        return $x;
    }
}
my $u;
say(1);
my $s = P->new->m . $u;
say(2);
