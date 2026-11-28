# kind: refused
# perl opens the file, and then reads the line.
use v5.42;
open(my $fh, '<', 'in.txt');
my @a;
my $o;
$a[open($o, '<', 'in.txt')] = <$fh>;
