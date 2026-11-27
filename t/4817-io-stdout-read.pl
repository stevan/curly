# kind: refused
# perl reads nothing, and warns: Filehandle STDOUT opened only for output.
use v5.42;
my $l = <STDOUT>;
