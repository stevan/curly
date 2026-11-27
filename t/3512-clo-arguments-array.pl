# kind: refused
# perl runs it: '2'.
use v5.42;
my $f = sub { scalar(@_) };
say $f->(1, 2);
