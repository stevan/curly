# kind: refused
# perl writes nothing, and warns: say() on unopened filehandle.
use v5.42;
my %h;
open(my $w, '>', 'o.txt') or die "no\n";
$h{fh} = $w;
$w = undef;
sub forget() {
    delete $h{fh};
    return 's';
}
say { $h{fh} } forget(), 't';
