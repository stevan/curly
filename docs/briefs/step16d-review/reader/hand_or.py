"""D260 by hand: EXPR or die, or return, or last, or next, and `and`."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from split import split

TEXT = r'''
sub f() { return 0; }
my $x = f() or die "no\n";
say "here";
----
sub f() { return 5; }
my $x = f() or die "no\n";
say $x;
----
my $y = 0;
my $x;
$x = $y or die "zero\n";
----
sub f() { return 0; }
sub g() { return 0; }
f() or g() or die "both\n";
----
sub f() { say "f"; return 0; }
sub g() { say "g"; return 1; }
f() or g() or die "both\n";
say "ok";
----
sub f() { say "f"; return 1; }
sub g() { say "g"; return 1; }
f() and g() or die "both\n";
say "ok";
----
sub f() { say "f"; return 0; }
sub g() { say "g"; return 1; }
f() and g() or die "both\n";
say "ok";
----
sub f() { say "f"; return 0; }
sub g() { say "g"; return 1; }
f() or g() and die "both\n";
say "ok";
----
sub f() { say "f"; return 1; }
sub g() { say "g"; return 1; }
f() or g() and die "both\n";
say "ok";
----
my $x = 0;
not $x or die "x\n";
say "ok";
----
my $x = 1;
not $x or die "x\n";
say "ok";
----
my $x = 1;
not $x and die "x\n";
say "ok";
----
my $x = 0; my $y = 1;
$x xor $y or die "x\n";
say "ok";
----
my $x = 0; my $y = 1;
$x or $y xor die "x\n";
say "ok";
----
say "a" or die "x\n";
----
print "a\n" or die "x\n";
----
say("a") or die "x\n";
----
sub f($x) { return $x or die "x\n"; }
say f(0);
----
sub f($x) { $x or return "none"; return "some"; }
say f(0); say f(1);
----
sub f($x) { $x or return; return "some"; }
say f(0) // "u"; say f(1);
----
sub f($x) { $x or return (1, 2, 3); return (4, 5); }
say join(",", f(0)); say join(",", f(1));
----
sub f($x) { $x or return (1, 2, 3); return 4; }
my $v = f(0);
say $v;
----
sub f($x) { $x and return 1, 2; return 4; }
my @v = f(1);
say "@v";
----
sub f($x) { $x or die "nope\n" }
say f(3);
----
sub f($x) { $x or die "nope\n" }
my $v = f(0);
----
sub f($x) { $x and return 7 }
say f(3);
say f(0);
----
sub f($x) { $x or return 7 }
say f(3);
----
sub f($x) { $x or return 7 }
say f(0);
----
sub f($x) { $x or return 7; }
my @l = (f(3));
say scalar(@l);
----
sub f($x) { $x and die "d\n" }
say f(0);
----
sub f($x) { $x and die "d\n" }
my @l = (f(0));
say scalar(@l);
say defined $l[0] ? "d" : "u";
----
sub f($x) { $x and die "d\n" }
my @l = (f(""));
say scalar(@l);
say "[$l[0]]";
----
sub f($x) { $x or die "d\n" }
my @l = (f("abc"), f(7));
say "@l";
----
sub f(@x) { @x or die "d\n" }
my @l = (f(1, 2, 3));
say "@l";
----
sub f(@x) { @x or return 0 }
my @l = (f(1, 2, 3));
say "@l";
----
sub f(@x) { @x or return 0 }
say f(1, 2, 3);
----
sub g() { return (4, 5, 6); }
sub f() { g() or die "d\n" }
my @l = f();
say "@l";
----
sub g() { return (4, 5, 6); }
sub f() { g() or die "d\n" }
say scalar(f());
----
sub g() { return (4, 5, 0); }
sub f() { g() or die "d\n"; return 1; }
say f();
----
sub g() { return (0, 0); }
g() or die "d\n";
say "ok";
----
sub g() { return (); }
g() or die "d\n";
say "ok";
----
sub g() { return; }
g() or die "d\n";
say "ok";
----
my @a = (0);
@a or die "d\n";
say "ok";
----
my @a = ();
@a or die "d\n";
say "ok";
----
my %h = ();
%h or die "d\n";
say "ok";
----
my @a = (1, 0);
(@a) or die "d\n";
say "ok";
----
my @a = (1, 0);
@a[0, 1] or die "d\n";
say "ok";
----
(1, 0) or die "d\n";
say "ok";
----
my ($x) = (0) or die "e\n";
say "here";
----
my @x = () or die "e\n";
say "here";
----
my ($x, $y);
($x, $y) = (0, 0) or die "e\n";
say "here";
----
my @a;
@a = () or die "e\n";
say "here";
----
my %h;
%h = () or die "e\n";
say "here";
----
my @a = (1);
my $n = @a or die "e\n";
say $n;
----
my @a = (1);
my $n = () = @a or die "e\n";
say $n;
----
my @a = (1, 2);
push @a, 3 or die "e\n";
say "@a";
----
my @a = ();
push @a, 0 or die "e\n";
say "@a";
----
my @a = (1, 2);
push(@a, 3) or die "e\n";
say "@a";
----
my @a = (0);
pop @a or die "e\n";
say "x";
----
my @a = (0);
shift(@a) or die "e\n";
say "x";
----
my $s = "a\n";
chomp $s or die "e\n";
say $s;
----
my $s = "a";
chomp($s) or die "e\n";
say $s;
----
my %h = (a => 0);
delete $h{a} or die "e\n";
----
my %h = (a => 0);
exists $h{a} or die "e\n";
say "ok";
----
my %h = (a => 0);
exists $h{b} or die "e\n";
say "ok";
----
my $x = 0;
$x++ or die "e\n";
----
my $x = 0;
++$x or die "e\n";
say $x;
----
my $x = 5;
$x -= 5 or die "e\n";
----
my $x;
$x //= 0 or die "e\n";
----
my $x = 0;
$x ||= 0 or die "e\n";
----
my $x = 0;
defined $x or die "e\n";
say "ok";
----
my $x = 0;
my $y = $x or die "y is zero\n";
----
my $x = 3;
my $y = $x or die "y is zero\n";
say $y;
----
my $x = 3;
my $y = $x or die "y is $y\n";
----
my $x = 3;
my $y = $x and say "in";
----
my $x = 0;
$x == 0 or die;
say "ok";
----
my $x = 1;
$x == 0 or die;
----
my $x = 1;
$x == 0 or die
  "over lines\n";
----
my $x = 1;
$x == 0
  or die "over lines\n";
----
my $x = 1;
$x == 0
  or die "over lines";
----
my $x = 1;
$x == 0 or
  die "over lines";
----
my $x = 1;
$x == 0 or die "a", "b";
----
my $x = 1;
$x == 0 or die("a\n");
----
my $x = 1;
$x == 0 or die("a\n") if 1;
----
my $x = 1;
$x == 0 or die "a\n" if $x;
----
my $x = 1;
$x == 0 or die "a\n" unless $x;
say "ok";
----
my $x = 1;
$x == 0 or die "a\n" for 1 .. 2;
----
for my $i (1 .. 5) { $i % 2 or next; say $i; }
----
for my $i (1 .. 5) { $i < 3 or last; say $i; }
----
for my $i (1 .. 5) { $i < 3 and next; say $i; }
----
OUT: for my $i (1 .. 3) { for my $j (1 .. 3) { $j < 2 or next OUT; say "$i$j"; } }
----
OUT: for my $i (1 .. 3) { for my $j (1 .. 3) { $i < 2 or last OUT; say "$i$j"; } }
----
my $i = 0;
while ($i < 5) { $i++; $i % 2 or next; say $i; }
----
my $i = 0;
while (true) { $i++; $i < 4 or last; }
say $i;
----
my $i = 0;
do { $i++; $i < 4 or last; } while (true);
say $i;
----
for my $k (1 .. 2) { my $i = 0; do { $i++; $i < 2 or next; say "in $k $i"; } while ($i < 4); say "after $k"; }
----
L: for my $k (1 .. 2) { my $i = 0; do { $i++; $i < 2 or next L; say "in $k $i"; } while ($i < 4); say "after $k"; }
----
my @l = map { $_ or die "zero\n" } (1, 2, 0);
----
my @l = map { $_ or die "zero\n" } (1, 2, 3);
say "@l";
----
my @l = map { $_ and die "zero\n" } (0, "", 0);
say scalar(@l);
----
my @l = grep { $_ > 1 or die "small\n" } (2, 3);
say "@l";
----
my @l = sort { $a <=> $b or die "tie\n" } (2, 3, 1);
say "@l";
----
my @l = sort { $a <=> $b or die "tie\n" } (2, 3, 2);
say "@l";
----
my @l = map { $_ or next } (1, 2, 0);
----
for my $i (1 .. 3) { my @l = map { $_ or next } (1, 0); say $i; }
----
sub f() { my @l = map { $_ or return 5 } (1, 0); return 6; }
say f();
----
my $x = 0;
$x or die;
----
my $x = 0;
$x or die
;
----
my $x = 0;
$x or warn "w\n";
say "ok";
----
my $x = 0;
$x or say "ok";
----
my $x = 0;
$x or $x = 5;
say $x;
----
my $x = 0;
$x or die "a\n" or die "b\n";
----
my $x = 0;
$x or die "a\n" and say "b";
----
my $x = 0;
$x or die "a\n", say "b";
----
my $x = 0;
$x || die "a\n";
----
my $x = 0;
my $y = $x || die "a\n";
----
my $x = 0;
my $y = $x // die "a\n";
say $y;
----
my $x;
my $y = $x // die "a\n";
----
my $x = 0;
($x or die "a\n");
----
my $x = 0;
if ($x or die "a\n") { say "in"; }
----
my $x = 1;
if ($x or die "a\n") { say "in"; }
----
my $x = 1;
$x and die "it is $x\n";
----
my $x = 1;
$x and die "it is ", $x, "\n";
----
sub f($x) { $x > 0 or return "neg"; $x < 10 or return "big"; return "ok"; }
say f(-1), f(50), f(5);
----
sub f($x) { $x > 0 or return "neg" if $x; return "ok"; }
say f(-1);
----
my $x = 0;
try { $x or die "caught\n"; } catch ($e) { print "c: $e"; }
----
my $x = 0;
try { $x or die { code => 5 }; } catch ($e) { say $e->{code}; }
----
my $x = 0;
$x or die { code => 5 };
----
my @a = (1, 2, 3);
my $n = @a or die "empty\n";
say $n;
----
my @a = (1, 2, 3);
my ($n) = @a or die "empty\n";
say $n;
----
my @a = (1, 2, 3);
my $x = $a[5] or say "none";
----
my $s = "abc";
my $i = index($s, "a") or say "at zero";
----
my $s = "abc";
substr($s, 0, 1, "X") or die "e\n";
----
my @a = (1,2);
$#a = 0 or die "e\n";
----
my $x = 1;
undef $x or die "e\n";
----
my $x = 1;
1 or die "e\n";
say "ok";
----
0 or die "e\n";
----
"a" and die "e\n";
----
my $x = 1;
$x = 0 or die "e\n";
----
my $x = 1;
$x = 2 or die "e\n";
say $x;
----
my $x = 1;
my $y = 5;
$x = $y - 5 or die "e\n";
----
my $x = 1;
($x = 0) or die "e\n";
----
my $x;
$x = undef or die "e\n";
----
my $x;
$x = "" or die "e\n";
----
my $x;
$x = "0.0" or say "false";
say "after";
----
my $x = 0;
$x or return;
say "after";
----
my $x = 0;
$x or last;
say "after";
----
sub f($x) { for my $i (1 .. 3) { $i == $x and return "found $i"; } return "none"; }
say f(2); say f(9);
----
sub f($x) { $x or
   return "none"; return "some"; }
say f(0);
----
my $h = { a => 1 };
$h->{b} or die "no b\n";
----
my $h = { a => 1 };
$h->{b}{c} or say "no c";
say join(",", sort keys $h->%*);
----
my $u;
$u->[0] or say "none";
----
my $x = "0E0";
$x or die "e\n";
say "true";
----
my $x = "00";
$x or die "e\n";
say "true";
----
my $x = 0.0;
$x or say "false";
----
my $x = "0";
$x and say "true";
say "end";
----
my @a = (1); my @b = ();
@a and @b or say "one empty";
----
my @a = (1); my @b = ();
@a or @b or say "both empty";
say "end";
----
sub f() { return wantarray2(); }
sub wantarray2() { return 1; }
f() or die;
say "ok";
----
my $x = 1;
$x or die "a" . "\n";
say "ok";
----
my $x = 0;
$x or die sprintf("%d\n", 5);
----
my $x = 0;
$x or
  die sprintf("%d\n", 5);
----
my $x = 0;
$x
  or die "a" . "b\n";
----
my $x = 0;
$x
  or die "a\n" . "b";
----
for my $i (1 .. 3) { $i == 2 and last }
say "ok";
----
for my $i (1 .. 3) { $i == 2 and next } continue { say "c"; }
----
my $i = 0;
{ $i++ or next; }
say $i;
----
my $i = 0;
if ($i == 0) { $i or last; }
----
for my $i (0, 1) { if ($i == 0) { $i or next; } say $i; }
----
sub f($x) { $x or return; 5 }
my @l = (f(0), f(1));
say scalar(@l);
----
sub f($x) { $x or return; 5 }
my $v = f(0);
say defined $v ? "d" : "u";
----
my $x = 0;
say "a" if $x or die "dead\n";
----
my $x = 0;
$x or do { say "in do"; };
----
my $x = 0;
$x or exit;
----
my $x = 0;
$x or die "a\n" x 2;
----
my $x = 0;
$x and next or die "odd\n";
'''


def cases():
    return split('o', TEXT)
