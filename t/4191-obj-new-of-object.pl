# kind: refused
# perl dies: Can't locate object method "new" via package "Object".
use v5.42;
use experimental 'class';
my $o = Object->new;
