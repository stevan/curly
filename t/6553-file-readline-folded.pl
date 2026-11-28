# kind: refused
# perl reads every line: the constant is folded away (T519).
use v5.42;
open(my $fh, '<', 'in.txt');
my @l = (0 || <$fh>);
