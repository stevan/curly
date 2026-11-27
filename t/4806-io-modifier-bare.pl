# kind: refused
# perl stores each line in its global $_.
use v5.42;
say "line" while <STDIN>;
