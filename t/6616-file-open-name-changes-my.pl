# kind: refused
# perl dies: Can't use an undefined value as filehandle reference: the sub below sees the my, and the handle perl made in it is gone.
use v5.42;
open(my $o, '<', 'in.txt') or die "no\n";
open(my $fh, '<', name()) or die "no\n";
sub name() {
    $fh = $o;
    return 'in.txt';
}
