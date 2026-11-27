# kind: refused
# perl dies: Can't use an undefined value as a symbol reference; a handle in $fh is step 21b's.
use v5.42;
my $fh;
say eof($fh) ? 1 : 0;
