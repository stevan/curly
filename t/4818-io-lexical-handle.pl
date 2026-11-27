# kind: refused
# perl warns: readline() on unopened filehandle; a handle in $fh is step 21b's.
use v5.42;
my $fh;
my $l = <$fh>;
