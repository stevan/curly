# kind: refused
# perl reads every line of stdin, each an argument.
use v5.42;
open(my $fh, '<', <STDIN>);
