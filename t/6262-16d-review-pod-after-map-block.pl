# kind: refused
# perl does not compile it: syntax error near "=" (T674).
use v5.42;
my @l = map {
    $_ * 2
}
=pod
=cut
1, 2;
say "@l";
