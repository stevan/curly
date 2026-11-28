# kind: refused
# perl does not compile it: syntax error near "=" (T674).
use v5.42;
my $i = 0;
for ($i = 0; $i < 2;
=pod
=cut
$i++) { }
say $i;
