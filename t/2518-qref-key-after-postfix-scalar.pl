# kind: refused
# perl runs it: 'HASH(0x...){a}\n'.
use v5.42;
my $h = {a => 1};
my $s = \$h;
say "$s->$*{a}";
