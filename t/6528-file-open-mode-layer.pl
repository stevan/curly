# kind: refused
# perl opens the file, its bytes as they are (T690).
use v5.42;
open(my $fh, '<:raw', 'in.txt');
