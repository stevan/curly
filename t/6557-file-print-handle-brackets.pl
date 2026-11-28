# kind: refused
# perl prints a to the file: after a handle the brackets are no argument list (T684).
use v5.42;
open(my $fh, '>', 'o.txt');
print $fh ("a");
