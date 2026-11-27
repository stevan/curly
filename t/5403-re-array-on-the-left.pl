# kind: refused
# perl warns: Applying pattern match (m//) to @a will act on scalar(@a) (T547).
use v5.42;
my @a = (1);
say @a =~ /1/ ? 1 : 0;
