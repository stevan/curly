# By hand (the independent review of step 21b; T698, D287): what open's variable holds is looked at before the
# file's name is worked out, as perl looks: perl dies there, Can't use string ("5") as a symbol ref, and the sub
# that gives the name is never called.
# kind: fault
# file: in.txt=a\n
use v5.42;
my $fh = 5;
sub name() {
    say "in name";
    return 'in.txt';
}
say "before";
open($fh, '<', name());
say "after";
