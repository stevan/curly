# kind: refused
# perl does not compile it: syntax error near "=" (T674).
use v5.42;
my @l = sort {
    $a <=> $b
}
=pod
=cut
2, 1;
say "@l";
