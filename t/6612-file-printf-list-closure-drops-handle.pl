# kind: refused
# perl writes nothing, and warns: printf() on unopened filehandle.
use v5.42;
open(my $w, '>', 'o.txt') or die "no\n";
my $f = sub {
    $w = undef;
    return 's';
};
printf $w '%s%s', $f->(), 't';
