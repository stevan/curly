# kind: refused
# perl reads the key's line first (T508).
use v5.42;
open(my $fh, '<', 'in.txt');
my %h;
$h{<$fh>} = <$fh>;
