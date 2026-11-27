use v5.42;
use experimental 'class';
class P { } my $o = P->new; say ref \$o; my $r = \$o; say ref $$r; say builtin::reftype(\$o); say builtin::reftype([1]), builtin::reftype({}), builtin::reftype(\1); say defined(builtin::blessed([1])) ? "b" : "u";
