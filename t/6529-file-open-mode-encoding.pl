# kind: refused
# perl opens the file as UTF-8: here `use open` says it for every file (D280).
use v5.42;
open(my $fh, '<:encoding(UTF-8)', 'in.txt');
