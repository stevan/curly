# kind: refused
# perl dies: Can't use an undefined value as filehandle reference (T698).
use v5.42;
my $fh;
sub pick() {
    $fh = undef;
    return 'in.txt';
}
open($fh, '<', pick()) or die "no\n";
