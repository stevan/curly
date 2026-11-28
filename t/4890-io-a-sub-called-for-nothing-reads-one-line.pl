# stdin: 1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n
# A sub that gives <STDIN> back, called for nothing, reads one line and
# not all that are left: perl hands "nothing wanted" on to the readline,
# through return, a last statement, a list, ? :, ||, x, and a call (T521).
use v5.42;
sub at() {
    my $e;
    try { die "now" } catch ($x) { $e = $x }
    print $e;
}
sub plain() { return <STDIN> }
sub last_statement() { <STDIN> }
sub listed() { return (<STDIN>, "x") }
sub twice() { return (<STDIN>, <STDIN>) }
sub repeated() { return (<STDIN>) x 3 }
sub chosen($c) { return $c ? <STDIN> : (<STDIN>, <STDIN>) }
sub other($c) { $c || <STDIN> }
sub handed() { return plain() }
sub among() { return (plain(), "x", twice()) }
sub sliced() { return (<STDIN>)[0] }
my $anon = sub { <STDIN> };
plain();
at();
last_statement();
at();
listed();
at();
twice();
at();
repeated();
at();
chosen(1);
at();
chosen(0);
at();
other(0);
at();
other(1);
at();
handed();
at();
among();
at();
$anon->();
at();
plain() for 1 .. 2;
at();
my @rest = plain();
say scalar(@rest);
at();
sliced();
at();
