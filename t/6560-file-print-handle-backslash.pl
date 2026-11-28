# kind: refused
# perl warns: Backslash found where operator expected (T684).
use v5.42;
my @a;
open(my $fh, '>', 'o.txt');
print $fh \@a;
