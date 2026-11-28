# kind: refused
# perl prints the line, and warns: Value of <HANDLE> construct can be "0"; test with defined() (T518).
use v5.42;
if (my $l = <STDIN>) {
    print $l;
}
