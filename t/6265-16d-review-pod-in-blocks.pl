# POD where a statement may begin inside the blocks of expressions, and after an if's block (T674: the places that stay in).
use v5.42;
my @l = map {
=pod
=cut
    my $q = $_;
=pod
=cut
    $q * 2 } 1, 2;
say "@l";
my $i = 0;
do {
=pod
=cut
    $i++;
=pod
=cut
} while ($i < 2);
say $i;
for ($i = 0; $i < 2; $i++) {
=pod
=cut
    say "in $i";
}
if ($i) { say "if"; }
=pod
=cut
else { say "else"; }
my $f = sub { my $v = 5;
=pod
=cut
    return $v; };
say $f->();
