"""D253, D251, D252 by hand."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from split import split

TEXT = r'''
my $i = 0;
do { my $j = $i; $i++; say $j; } while ($i < 3);
----
my $i = 0;
do { my $j = $i; $i++; } while ($j < 3);
----
my $j = 10; my $i = 0;
do { my $j = $i; $i++; say $j; } while ($j < 3);
say $i;
----
my $j = 0; my $i = 0;
do { my $j = $i; $i++; } until ($j++ > 3);
say "$i $j";
----
my $i = 0;
do { $i++ } while ($i < 3);
say $i;
----
my $i = 0;
do { $i++ } until ($i >= 3);
say $i;
----
my $i = 0;
do { $i++; } while $i < 3;
say $i;
----
my $i = 0;
do { $i++; } until $i;
say $i;
----
my $i = 0;
do { $i++; } if $i == 0;
say $i;
----
my $i = 0;
do { $i++; } unless $i;
say $i;
----
my $i = 0;
do { $i++; } for 1 .. 3;
say $i;
----
my $i = 0;
do { $i++; };
say $i;
----
my $i = 0;
my $x = do { $i++; 5 } while ($i < 3);
----
my $i = 0;
do { $i++; } while ($i < 3) or die "x\n";
----
my $i = 0;
do { $i++; } while ($i < 3), say "x";
----
my $i = 0;
do { $i++; } while ($i < 3) + 1;
say $i;
----
my $i = 0;
do { $i++; } while (($i < 3) + 1 < 2);
say $i;
----
my $i = 0;
do { $i++; } while ($i < 3) && $i != 2;
say $i;
----
my $i = 0;
do { $i++; } while $i < 3 and $i != 2;
say $i;
----
my $i = 0;
do { $i++; } while not $i > 3;
say $i;
----
my $i = 0;
do { do { $i++; } while ($i % 3); say $i; } while ($i < 9);
----
my $i = 0;
OUT: for my $k (1 .. 3) { do { $i++; next OUT if $i == 2; say "$k $i"; } while ($i < 4); }
----
my $i = 0;
OUT: for my $k (1 .. 3) { do { $i++; last OUT if $i == 2; say "$k $i"; } while ($i < 4); }
say $i;
----
my $i = 0;
for my $k (1 .. 3) { do { $i++; next if $i == 2; say "$k $i"; } while ($i < 4); }
----
my $i = 0;
do { $i++; last if $i == 2; } while ($i < 4);
----
my $i = 0;
while ($i < 10) { do { $i++; last; } while ($i < 4); }
----
my $i = 0;
do { for my $k (1 .. 3) { next if $k == 2; last if $k == 3; $i++; } } while ($i < 4);
say $i;
----
sub f() { my $i = 0; do { $i++; return $i if $i == 2; } while ($i < 5); return -1; }
say f();
----
sub f() { my $i = 0; do { $i++; } while ($i < 5) }
say f();
----
sub f() { my $i = 0; do { $i++; } while ($i < 5); }
my @l = (f());
say scalar(@l);
----
sub f() { my $i = 0; do { $i++; } until ($i == 5) }
my $v = f();
say $v;
----
my $i = 0;
L: do { $i++; } while ($i < 3);
----
my $i = 0;
do { $i++; } while (my $z = $i < 3);
----
my $i = 0;
do { $i++; say "b"; } while (warn "w\n");
----
my $i = 0;
do { $i++; say "b"; } while ($i < 2 and warn "w\n");
----
my $i = 0;
do { $i++; say "b"; } until ($i > 1 or die "d\n");
----
sub t() { die "in t\n"; }
my $i = 0;
do { $i++; say "b"; } while (t());
----
my $i = 0;
do { $i++; say "b"; } while ($i < 2 ? true : die "d\n");
----
my @a = (1, 2, 3);
do { say shift @a; } while (@a);
----
my @a = (1, 2, 3);
do { say shift @a; } until (!@a);
----
my @a = (1, 2, 3);
do { say pop @a } while @a;
----
my @a = ();
do { say defined(shift @a) ? "d" : "u" } while (@a);
----
my $i = 5;
do { say $i; } while ($i-- > 3);
----
my $i = 0;
do { $i++; } while ($i < 3); say $i;
----
my $i = 0;
do {
  $i++;
  die "at three" if $i == 3;
}
while ($i < 5);
----
my $i = 0;
my $u;
do {
  $i++;
}
while ($i + $u < 5);
----
my $i = 0;
my $u;
do {
  $i++;
} while (
  $i + $u < 5);
----
my $i = 0;
do {
  $i++;
} until (
  $i / 0);
----
my $i = 0;
do { $i++; } while ($i < 3) if 1;
----
my $i = 0;
do { $i++; } while ($i < 3) while (0);
----
my $i = 0;
do { $i++; } while 0;
say $i;
----
my $i = 0;
do { $i++; } until 1;
say $i;
----
my $i = 0;
do { $i++; } while ();
----
my $i = 0;
do { $i++; } while (());
say $i;
----
my $i = 0;
do { } while ($i++ < 3);
say $i;
----
my $i = 0;
do { 1 } while ($i++ < 3);
say $i;
----
my $i = 0;
do { $i } while ($i++ < 3);
say $i;
----
my $i = 0;
do { $i++; $i } while ($i < 3);
say $i;
----
my $i = 0;
do { say "x"; "abc" } while ($i++ < 1);
----
my $i = 0;
do { $i++ ; say "x" if $i > 1 } while ($i < 3);
----
my $i = 0;
do { +{ a => 1 } } while ($i++ < 1);
say $i;
----
my $i = 0;
do { a => 1 } while ($i++ < 1);
say $i;
----
my $i = 0;
do { "a", 1 } while ($i++ < 1);
say $i;
----
my $i = 0;
do { ; } while ($i++ < 1);
say $i;
----
my $i = 0;
do { $i++; { last; } say "after bare"; } while ($i < 2);
----
my $i = 0;
do { $i++; try { die "x\n" if $i == 1; } catch ($e) { print "c$e"; } } while ($i < 2);
----
my $i = 0;
my @s;
do { my $k = $i; push @s, sub { return $k; }; $i++; } while ($i < 3);
say join(",", map { $_->() } @s);
----
my $i = 0;
my @r;
do { my $k = $i; push @r, \$k; $i++; } while ($i < 3);
say join(",", map { $_->$* } @r);
----
my $i = 0;
do { my @a; push @a, $i; say scalar(@a); $i++; } while ($i < 3);
----
my $i = 0;
do { my $x; $x .= "a"; say $x; $i++; } while ($i < 3);
----
my @a = (1, 2, 3);
for my $x (@a) { my $i = 0; do { $i++; } while ($i < $x); say $i; }
----
my @a = (1, 2, 3);
for my $x (@a) { do { push @a, 1; } while (0); last; }
----
my $i = 0;
do { $i++ } while ($i < 3) ;
do { $i++ } until ($i > 5) ;
say $i;
----
my $i = 0;
do
{ $i++ }
while ($i < 3);
say $i;
----
my $i = 0;
do{$i++}while($i<3);
say $i;
----
my $i = 0;
do { $i++ } while($i<3)
;
say $i;
----
my $i = 0;
if ($i == 0) { do { $i++ } while ($i < 3) }
say $i;
----
my $i = 0;
do { $i++ } while $i < 3 ? true : false;
say $i;
----
my @a = (1, 2, 3);
$#a = 5;
say scalar(@a), defined $a[4] ? "d" : "u";
----
my @a = (1, 2, 3);
$#a = 0;
say "@a";
$#a = -1;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = -2;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = 1.7;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = -0.5;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = -1.5;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = "1";
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = "1.9";
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = "abc";
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = "1abc";
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = " 1";
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = "1e0";
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = "0x1";
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = "";
say scalar(@a);
----
my @a = (1, 2, 3);
my $u;
$#a = $u;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = true;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = false;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = [1];
----
my @a = (1, 2, 3);
$#a = $#a;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = $#a - 1;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = @a;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = pop @a;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = shift @a;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = push(@a, 1);
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = ($a[5] = 1);
say scalar(@a);
----
my @a = (1, 2, 3);
my @b = (1);
$#a = $#b = 4;
say scalar(@a), scalar(@b);
----
my @a = (1, 2, 3);
$#a += 2;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a++;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a--;
say scalar(@a);
----
my @a = (1, 2, 3);
my $x = ($#a = 0);
say $x;
----
my @a = (1, 2, 3);
($#a) = 0;
say scalar(@a);
----
my @a = (1, 2, 3);
my $r = \@a;
$#a = 0;
say scalar($r->@*);
$r->$#* = 4;
say scalar(@a);
$#{$r} = 1;
say scalar(@a);
$#$r = 0;
----
my @a = ([1], [2], [3]);
my $keep = $a[2];
$#a = 0;
$#a = 2;
say defined $a[2] ? "d" : "u";
say $keep->[0];
----
my @a = (1, 2, 3);
my $keep = \@a;
for my $x (@a) { $#a = 5; }
----
my @a = (1, 2, 3);
for my $x (@a) { $#a = 2; }
say "ok";
----
my @a = (1, 2, 3);
my @k = map { $#a = 2; $_ } @a;
say "@k";
----
my $r;
$#{$r} = 2;
say scalar($r->@*);
----
my $r;
$r->$#* = -1;
say ref($r);
----
my $r;
$#{$r} = -2;
say ref($r);
----
my $r = {};
$#{$r} = 2;
----
my $r = 5;
$#{$r} = 2;
----
my %h;
$#{$h{list}} = 1;
say scalar($h{list}->@*);
----
my %h;
$h{list}->$#* = 1;
say scalar($h{list}->@*);
----
my @a;
$#{$a[2]} = 0;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = 1 if @a > 2;
say "@a";
----
my @a = (1, 2, 3);
$#a = 0 for 1 .. 2;
say "@a";
----
my @a = (1, 2, 3);
$#a = 4, say "x";
----
my @a = (1, 2, 3);
say $#a = 0;
----
my @a = (1, 2, 3);
sub f() { $#a = 0 }
say f();
----
my @a = (1, 2, 3);
sub f() { $#a = 0; }
my @l = (f());
say scalar(@l);
----
my @a = (1, 2, 3);
sub f() { $#a = 0; }
f();
say "@a";
----
my @a = (1, 2, 3);
$#a = 9223372036854775807;
----
my @a = (1, 2, 3);
$#a = 1e3;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = 1e30;
----
my @a = (1, 2, 3);
$#a = -1e30;
----
my @a = (1, 2, 3);
$#a = -1.0;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = "-1";
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = -0.0;
say scalar(@a);
----
my @a = (1, 2, 3);
$#a = "-0.9";
say scalar(@a);
----
my @a = (1, 2, 3);
say "$#a";
$#a = 0;
say "$#a";
----
my @a = (1, 2, 3);
($a[0], $#a) = (9, 0);
say "@a";
----
my @a = (1, 2, 3);
$#a = 0; $a[2] = 7;
say defined $a[1] ? "d" : "u";
----
my @a = (1, 2, 3);
$# a = 0;
----
my @a = (1, 2, 3);
$#{a} = 0;
say "@a";
----
my @a = (1, 2, 3);
$#a = $a[0] + ($#a = 0);
----
my @a = (1, 2, 3);
my @b = (@a, ($#a = 0));
----
my $x = 5;
undef $x;
say defined $x ? "d" : "u";
----
my $x = 5;
undef($x);
say defined $x ? "d" : "u";
----
my @a = (1, 2);
undef @a;
say scalar(@a);
----
my %h = (a => 1);
undef %h;
say scalar(%h);
----
my @a = (1, 2);
undef $a[0];
say defined $a[0] ? "d" : "u", scalar(@a);
----
my @a = (1, 2);
undef $a[5];
say scalar(@a);
----
my @a = (1, 2);
undef $a[-1];
say defined $a[1] ? "d" : "u", scalar(@a);
----
my @a = (1, 2);
undef $a[-5];
say scalar(@a);
----
my %h = (a => 1);
undef $h{a};
say exists $h{a} ? "e" : "n", defined $h{a} ? "d" : "u";
----
my %h = (a => 1);
undef $h{b};
say exists $h{b} ? "e" : "n";
----
my $r;
undef $r->[1];
say scalar($r->@*);
----
my $r;
undef $r->{a}{b};
say join(",", sort keys $r->%*), exists $r->{a}{b} ? "e" : "n";
----
my $r;
undef @{$r};
say ref($r);
----
my $r;
undef $r->@*;
say ref($r);
----
my $r;
undef %{$r};
say ref($r);
----
my $r;
undef $r->%*;
say ref($r);
----
my $r;
undef $r->$*;
say ref($r);
----
my $r;
undef ${$r};
say ref($r);
----
my $r = [1];
undef @{$r};
say scalar($r->@*);
----
my $r = [1];
undef %{$r};
----
my $r = 5;
undef @{$r};
----
my $x = 5;
my $r = \$x;
undef $x;
say defined $r->$* ? "d" : "u";
----
my $x = 5;
my $r = \$x;
undef $r->$*;
say defined $x ? "d" : "u";
----
my $x = 5;
my $r = \$x;
undef $r;
say $x;
----
for my $x (1, 2) { undef $x; }
----
my @a = (1, 2);
for my $x (@a) { undef $x; }
say defined $a[0] ? "d" : "u";
----
for (1, 2) { undef $_; }
----
for (1, 2) { undef; }
----
my @l = map { undef $_; 1 } (1, 2);
----
my @l = sort { undef $a; 0 } (1, 2);
----
sub f($p) { undef $p; return defined $p ? "d" : "u"; }
my $v = 5;
say f($v), $v;
----
sub f(@p) { undef @p; return scalar(@p); }
say f(1, 2);
----
my @a = (1, 2);
for my $x (@a) { undef @a; }
----
my @a = (1, 2);
for my $x (@a) { undef $a[0]; }
----
my %h = (a => 1);
for my $v (values %h) { undef %h; }
----
my %h = (a => 1);
for my $v (values %h) { undef $h{a}; }
----
my %h = (a => 1);
for my $k (keys %h) { undef $h{$k}; }
say defined $h{a} ? "d" : "u";
----
my @a = (1, 2);
for my $i (0 .. $#a) { undef @a; }
say scalar(@a);
----
my ($x, $y) = (1, 2);
undef $x, $y;
----
my ($x, $y) = (1, 2);
undef($x, $y);
----
my ($x, $y) = (1, 2);
undef($x), undef($y);
----
my $x = 1;
say undef($x) + 1;
----
my $x = 1;
my $y = undef $x;
----
my $x = 1;
my $y = undef($x);
----
my $x = 1;
my @l = (undef $x);
----
my $x = 1;
say defined(undef $x) ? "d" : "u";
----
my $x = 1;
undef $x if $x;
say defined $x ? "d" : "u";
----
my $x = 1;
undef $x unless $x;
say defined $x ? "d" : "u";
----
my @a = (1, 2, 3);
undef $_ for @a;
----
my @a = (1, 2, 3);
undef $a[$_] for 0 .. $#a;
say scalar(grep { defined $_ } @a);
----
my $x = 1;
undef $x while $x;
say "ok";
----
sub f() { my $x = 1; undef $x }
say defined f() ? "d" : "u";
----
sub f() { my $x = 1; undef $x; }
my @l = (f());
say scalar(@l);
----
sub f() { my @x = (1); undef @x }
my @l = (f());
say scalar(@l);
----
my @a = (1, 2, 3);
undef @a[0, 1];
----
my %h = (a => 1);
undef @h{"a"};
----
my @a = (1, 2, 3);
undef $#a;
----
my @a = (1, 2, 3);
undef scalar(@a);
----
my @a = (1, 2, 3);
undef (@a);
say scalar(@a);
----
my @a = (1, 2, 3);
undef(@a);
say scalar(@a);
----
my @a = (1, 2, 3);
undef @a, say "x";
----
my $x = 1;
undef $x; undef $x;
say "ok";
----
my $x = 1;
undef
  $x;
say defined $x ? "d" : "u";
----
my $x = 1;
undef $x
;
say defined $x ? "d" : "u";
----
my $x = 1;
undef +$x;
----
my $x = 1;
undef ($x);
say defined $x ? "d" : "u";
----
my $x = 1;
undef ($x) + 1;
----
my $x = 1;
undef($x) || say "u";
----
my $x = 1;
undef $x or say "u";
----
my $x = 1;
undef $x . "a";
----
my $x = 1;
undef $x = 5;
----
my $x = "abc";
my $y = $x;
undef $x;
say $y;
----
my @a = ([1, 2]);
my $in = $a[0];
undef @a;
say "$in->@*";
----
my %h = (a => 1);
my $r = \%h;
undef %h;
say scalar($r->%*);
$r->{b} = 2;
say scalar(%h);
----
my @a = (1);
my $r = \@a;
undef @a;
push @a, 5;
say "$r->@*";
----
my $f = sub { return 1; };
undef $f;
say defined $f ? "d" : "u";
----
sub f() { return 1; }
undef &f;
----
undef;
----
my $x = undef;
undef $x;
say "ok";
----
my $x = 5;
my @s = (sub { return $x; });
undef $x;
say defined $s[0]->() ? "d" : "u";
----
my $x = 5;
undef my $y;
----
undef my $y;
say "ok";
----
my %h = (a => { b => 1 });
undef $h{a}{b};
say exists $h{a}{b} ? "e" : "n";
----
my %h = (a => { b => 1 });
undef $h{a}->%*;
say scalar($h{a}->%*);
----
my %h = (a => { b => 1 });
undef %{$h{a}};
say scalar($h{a}->%*);
----
my %h;
undef %{$h{a}};
say exists $h{a} ? "e" : "n";
----
my %h;
undef @{$h{a}{b}};
say join(",", sort keys %h), ref($h{a}{b});
'''


def cases():
    return split('d', TEXT)
