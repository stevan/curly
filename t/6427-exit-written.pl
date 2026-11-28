# t/models/file.py 6427
# kind: warns
use v5.42;
open(my $out, '>', "o.txt") or die "cannot open o.txt: $!\n";
print $out "written\n";
close($out);
open($out, '>>', "o.txt");
die "written, closed, and opened again\n";
