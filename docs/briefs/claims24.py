# Step 24's statements about perl, as claims.py's rows: what perl does
# with each construct that examples/BENDS.md records the language
# refusing or faulting, and with the five it recommends loosening.
# claims.py reads it.
#
#     python3 docs/briefs/claims.py E24-int E24-split
def c(id, where, code, **said):
    return (id, where, code, said)

STEP24 = [
    # ---- not in the language yet (BENDS.md, "Not yet": steps 19, 20, 22)
    c('E24-int', 'BENDS; PLAN 24', 'say int(7 / 2), " ", int(-7 / 2), " ", int(2.999);', out='3 -3 2\n'),
    c('E24-abs', 'BENDS; PLAN 24', 'say abs(-3), " ", abs(2.5);', out='3 2.5\n'),
    c('E24-split', 'BENDS; PLAN 24', 'my @c = split //, "abc"; say "@c"; my @w = split " ", "  a b  c "; say scalar(@w); my @f = split /,/, "x,y,,z"; say "@f";', out='a b c\n3\nx y  z\n'),
    c('E24-split-dot', 'BENDS; PLAN 24', 'my @f = split /./, "a.b"; say scalar(@f);', out='0\n'),
    c('E24-regex', 'BENDS; PLAN 24', 'my $t = "42"; say $t =~ /^\\d+(\\.\\d+)?$/ ? "number" : "not";', out='number\n'),
    # ---- refused or faulted by a decision (BENDS.md, "By decision")
    c('E24-a-param', 'BENDS; D55', 'sub gcd ($a, $b) { return $b == 0 ? $a : gcd($b, $a % $b) } say gcd(48, 18);', out='6\n'),
    c('E24-scalar', 'BENDS; PLAN 9', 'my @a = (1, 2, 3); my %h = (a => 1); say scalar @a; say scalar keys %h; say scalar @a + 1; say scalar(grep { $_ > 1 } @a); say scalar @a == 3 ? "three" : "no";', out='3\n1\n4\n2\nthree\n'),
    c('E24-sort-brackets', 'BENDS; D89', 'my %h = (b => 1, a => 2); say join ",", sort(keys %h); sub letters ($w) { return split //, $w } say join "", sort(letters("cab"));', out='a,b\nabc\n'),
    c('E24-sort-name', 'BENDS; D89; T190', 'sub letters ($w) { return split //, $w } say join "", sort letters("cab");', out='cab\n'),
    c('E24-sort-blank', 'BENDS; D89; T190', 'my @a = (2, 1); my @s = (sort (@a), 9); say "@s";', out='1 2 9\n', err='sort \\(\\.\\.\\.\\) interpreted as function'),
    c('E24-or-die', 'BENDS; D56; D146', 'my %ops = (a => 1); my $f = $ops{a} or die "no\\n"; say $f; my $g = $ops{b} or die "unknown b\\n";', out='1\n', exit=255, err='^unknown b\\n$'),
    c('E24-or-return', 'BENDS; D56; T139', 'sub h ($x) { my $n = $x or return "none"; return "got $n" } say h(0), " ", h(5);', out='none got 5\n'),
    c('E24-transpose', 'BENDS; D114; T249', 'sub transpose ($m) { my @t; for my $i (0, 1) { for my $j (0, 1) { $t[$j][$i] = $m->[$i][$j] } } return \\@t } say join ";", map { join ",", $_->@* } transpose([[1, 2], [3, 4]])->@*;', out='1,3;2,4\n'),
    c('E24-transpose-alias', 'BENDS; D114; T249', 'my @t = (undef); my $m = [\\@t]; $t[0][0] = $m->[0][0]; say ref $t[0][0], " ", $t[0][0] == $t[0] ? "itself" : "other";', out='ARRAY itself\n'),
    c('E24-die-sprintf', 'BENDS; D150', 'my $n = 1;\ndie sprintf("has %d\\n", $n)\n    if $n;', out='', exit=255, err='^has 1\\n$'),
    c('E24-die-concat', 'BENDS; D150', 'my @l = (1, 2);\ndie "cycle among: " . join(" ", @l) . "\\n"\n    if @l;', out='', exit=255, err='^cycle among: 1 2\\n$'),
    c('E24-range-numeric-string', 'BENDS; D80; T154', 'my $n = "7"; my @x = (1 .. $n); say scalar(@x); my @c = (1, qw(3)); say join ",", 1 .. $c[1];', out='7\n1,2,3\n'),
    c('E24-range-letters', 'BENDS; D80; T154', "say join ',', ('a' .. 'e');", out='a,b,c,d,e\n'),
    c('E24-subsep', 'BENDS; D22', 'say join($;, "a", "b") eq "a\\x{1c}b" ? "FS" : "no";', out='FS\n'),
    c('E24-count-of', 'BENDS; D78', 'my $n = () = (5, 6, 7); say $n; say scalar(() = grep { $_ } (0, 1, 2));', out='3\n2\n'),
    c('E24-memo', 'BENDS; D76; D163', 'my %c; my $f = sub ($n) { $n * 2 }; sub m1 ($k) { return $c{$k} //= $f->($k) } say m1(4), m1(4);', out='88\n'),
    c('E24-deep-recursion', 'BENDS; D67', 'sub c ($n) { return if $n == 1; c($n % 2 ? 3 * $n + 1 : $n / 2) } c(27); say "ok";', out='ok\n', err='Deep recursion on subroutine "main::c"'),
    c('E24-undef-compare', 'BENDS; D48', 'my %v = (I => 1); my $n = $v{Q}; say 1 < $n ? "y" : "n";', out='n\n', err='Use of uninitialized value \\$n in numeric lt'),
    c('E24-comma-return', 'BENDS; D15', 'sub k ($c) { my $buf; $buf = $c, return "n" if $c eq "1"; return "x" } say k("1"), k("2");', out='nx\n'),
    c('E24-ucfirst-lc', 'BENDS; D85', 'say join " ", map { ucfirst lc } qw(aB cD);', out='Ab Cd\n'),
    c('E24-say-for', 'BENDS; D85', 'my @o = (1, 2); say for @o;', out='1\n2\n'),
    c('E24-reverse-scalar', 'BENDS; D84', 'my $c = "abc"; say $c eq reverse($c) ? "p" : "n"; say scalar reverse "abc";', out='n\ncba\n'),
    c('E24-lvalue-substr', 'BENDS; D17; D56', 'my $t = "abc"; substr($t, 1, 1) = "X"; say $t;', out='aXc\n'),
    c('E24-loop-variable', 'BENDS; D17', 'my @d = (1, 2); for my $x (@d) { $x *= 2 } say "@d";', out='2 4\n'),
    c('E24-insertion', 'BENDS; D17; D81', 'my @a = (3, 1, 2); for my $i (1 .. $#a) { my $v = $a[$i]; my $j = $i - 1; while ($j >= 0 && $a[$j] > $v) { $a[$j + 1] = $a[$j]; $j-- } $a[$j + 1] = $v } say "@a";', out='1 2 3\n'),
    c('E24-do-block', 'BENDS; D58', 'my %l; sub d ($n) { return $l{$n} //= do { $n * 2 } } say d(3), d(3);', out='66\n'),
    c('E24-printf-concat', 'BENDS; D124', 'printf "%2s" . "%3d" x 2 . "\\n", "x", 1, 2;', out=' x  1  2\n'),
    c('E24-interp-index', 'BENDS; D91', 'my @m = qw(Jan Feb); my $i = 2; say "$m[$i - 1] 2026";', out='Feb 2026\n'),
    c('E24-deref-bare', 'BENDS; D108', 'my $r = [1, 2]; my $h = {a => 1}; say scalar(@$r), $#$r, join(",", %$h), "@$r[0, 1]";', out='21a,11 2\n'),
    c('E24-eval', 'BENDS; D20', 'eval { die "x\\n" }; print "caught: $@";', out='caught: x\n'),
    c('E24-rational-overflow', 'BENDS; D35', 'my ($n, $d) = (1, 1); my ($tn, $td) = (1, 1); for my $k (1 .. 15) { $td *= $k; my ($p, $q) = ($n * $td + $tn * $d, $d * $td); my ($x, $y) = ($p, $q); ($x, $y) = ($y, $x % $y) while $y; ($n, $d) = ($p / $x, $q / $x); } say "$n/$d";',
      outre='[0-9.e+]+/[0-9.e+]+\n'),
]
