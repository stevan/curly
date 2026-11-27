# kind: refused
# perl reads <0.5 ... as a glob.
use v5.42;
say "y" if rand < 0.5;
