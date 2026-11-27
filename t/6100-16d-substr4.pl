# substr of four arguments, as a statement: the piece three would take, replaced (D254).
use v5.42;
my $s = "abcdef";
substr($s, 1, 2, "XYZ");
say $s;
substr($s, -2, 1, "");
say $s;
substr($s, 0, 0, "<");
say $s;
my $t = "abc";
substr($t, 3, 1, "x");
say $t;
substr($t, 1, -1, "Q");
say $t;
substr($t, 1, 99, "");
say $t;
my $n = 12345;
substr($n, 1, 1, 9);
say $n + 1;
substr($t, 0, 1, "Z") if 1;
say $t;
my $u = "hello";
my $k = substr($u, 1, 3);
substr($u, 1, 3, "EEE");
say "$k $u";
sub up($w) {
    my $c = $w;
    substr($c, 0, 1, uc(substr($c, 0, 1)));
    return $c;
}
say up("word");
