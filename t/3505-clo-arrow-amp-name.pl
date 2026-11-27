# kind: refused
# perl dies: Undefined subroutine &main::g (a call of g with $f first, as a lexical method is called).
use v5.42;
my $f = sub { 1 };
$f->&g();
