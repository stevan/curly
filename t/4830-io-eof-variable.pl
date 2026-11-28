# kind: refused
# perl dies: Can't use an undefined value as a symbol reference.
use v5.42;
my $fh;
say eof $fh ? 1 : 0;
