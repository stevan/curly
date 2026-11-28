"""D250, D258, D262, D254, D255, D261 by hand."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from split import split

TEXT = r'''
my @a = (1, 2, 3);
say scalar @a;
say scalar(@a) x 3;
say scalar @a, "x";
say scalar @a == 3 ? "y" : "n";
say scalar @a < 5;
say scalar @a ? "t" : "f";
say scalar @a && "and";
say scalar @a || "or";
say scalar @a // "dor";
say scalar @a <=> 2;
say scalar @a eq "3";
say scalar @a .. 4;
----
my @a = (1, 2, 3);
say scalar @a + 1;
----
my @a = (1, 2, 3);
say scalar @a . "x";
----
my @a = (1, 2, 3);
say scalar @a x 2;
----
my @a = (1, 2, 3);
say scalar @a * 2;
----
my @a = (1, 2, 3);
say scalar @a ** 2;
----
my @a = (1, 2, 3);
say scalar @a - 1;
----
my @a = (1, 2, 3);
say scalar @a -1;
----
my @a = (1, 2, 3);
say scalar @a [1];
----
my @a = (1, 2, 3);
say scalar @a[1];
----
my @a = (1, 2, 3);
say scalar @a[0, 1];
----
my %h = (a => 1);
say scalar %h;
say scalar keys %h;
say scalar values %h;
say scalar %h ? "t" : "f";
----
my %h = (a => 1, b => 2);
say scalar @h{"a", "b"};
----
my %h = (a => 1, b => 2);
say scalar %h{"a"};
----
my %h = (a => 1, b => 2);
say scalar keys %h + 1;
----
my $r = [1, 2];
say scalar $r->@*;
say scalar @{$r};
say scalar @$r;
----
my $r = [1, 2];
say scalar $r->@* + 1;
----
my $r = [1, 2];
say scalar $r->@[0, 1];
----
my $r = [1, 2];
say scalar @{$r}[0];
----
my $r = [[1, 2]];
say scalar $r->[0]->@*;
say scalar $r->[0]@*;
----
my $r = [[1, 2]];
say scalar @{$r->[0]};
say scalar @{ $r->[0] } == 2 ? "y" : "n";
----
my $r = {a => 1};
say scalar $r->%*;
say scalar %{$r};
say scalar keys $r->%*;
say scalar keys %{$r};
----
my @a = (1, 2);
my $x = scalar @a;
my @b = (scalar @a, scalar @a);
say "$x @b";
----
my @a = (1, 2);
sub f($n) { return $n * 2; }
say f(scalar @a);
say f scalar @a;
----
my @a = (1, 2);
say scalar @a, scalar @a;
say scalar(@a), scalar @a;
----
my @a = (1, 2);
say "n: " . scalar @a;
say "n: " . scalar @a . "!";
----
my @a = (1, 2);
my @b = (3);
say scalar @a, @b;
----
my @a = (1, 2);
say scalar @a if scalar @a;
say "x" unless scalar @a > 5;
----
my @a = (1, 2);
for my $i (1 .. scalar @a) { say $i; }
----
my @a = (1, 2);
say scalar @a =~ 2;
----
my @a = (1, 2);
say scalar
  @a;
----
my @a = (1, 2);
say scalar (@a);
say scalar (@a) + 1;
----
my @a = (1, 2);
say scalar(@a) + 1;
say scalar(@a)[0];
----
my @a = (1, 2);
say scalar @a ? scalar @a : 0;
----
my @a = (1, 2);
say -scalar @a;
say !scalar @a;
----
my @a = (1, 2);
say scalar @a++;
----
my @a = (1, 2);
say scalar @a->[0];
----
my @a = (1, 2);
say scalar @a = (1);
----
my @a = (1, 2);
my $n = scalar @a = (1, 2, 3);
----
my @a = (1, 2);
say scalar @a , 5;
----
my $x = 5;
say scalar $x;
----
say scalar "abc";
----
say scalar (1, 2, 3);
----
my @a = (1, 2);
say scalar @a and say "t";
----
my @a = (1, 2);
say scalar push @a, 1;
----
my @a = (1, 2);
say scalar grep { $_ > 1 } @a;
----
my @a = (1, 2);
say scalar map { $_ } @a;
----
my @a = (1, 2);
say scalar sort @a;
----
my @a = (1, 2);
say scalar @a[0 .. 1];
----
my @a = (1, 2);
say scalar splice(@a, 0, 1);
----
my @a = (1, 2);
say scalar pop @a;
----
my @a = (1, 2);
say scalar defined $a[0];
----
my @a = (1, 2);
say scalar @a lt 3;
say scalar @a x= 2;
----
my @a = (1, 2);
say scalar @a x 2;
----
my @a = (1, 2);
say scalar @a  => 5;
----
my @a = (1, 2);
my %h = (scalar @a => 5);
say join(",", %h);
----
say scalar reverse "abc";
say scalar reverse "abc", "def";
say scalar reverse("abc", "def");
say scalar(reverse "abc");
say scalar(reverse("abc", "def"));
----
my @a = ("ab", "cd");
say scalar reverse @a;
say scalar reverse @a, "x";
----
my @a = ();
say scalar reverse @a;
----
say scalar reverse;
----
say scalar reverse();
----
for ("abc") { say scalar reverse; }
----
for ("abc") { say scalar reverse(); }
----
for ("abc") { say scalar reverse $_; }
----
sub f() { return ("ab", "cd"); }
say scalar reverse f();
----
sub f() { return; }
say scalar reverse f();
----
sub f() { return "xyz"; }
say scalar reverse f();
----
say scalar reverse "abc" . "def";
----
say scalar reverse("abc") . "def";
----
say scalar reverse "abc" x 2;
----
say scalar reverse 123;
say scalar reverse 1.5, 2;
say scalar reverse true;
----
my $u;
say scalar reverse $u;
----
my $u;
say scalar reverse "a", $u;
----
say scalar reverse "héllo";
say scalar reverse "a\x{301}b";
----
say scalar reverse [1];
----
say scalar reverse 1 .. 3;
say scalar reverse "a" .. "c";
----
say scalar reverse reverse "abc", "def";
----
say scalar reverse sort "b", "a";
----
say scalar reverse map { $_ x 2 } "ab", "c";
----
my $s = scalar reverse "abc";
my @l = (scalar reverse("ab"), "z");
say "$s @l";
----
my $s = "abc";
say lc scalar reverse $s;
say length scalar reverse $s;
----
my $s = "abc";
say scalar reverse $s eq "cba" ? "y" : "n";
----
my $s = "abc";
say scalar reverse($s) eq "cba" ? "y" : "n";
----
my $s = "abc";
say "pal" if $s eq scalar reverse $s;
say "not" unless $s eq scalar reverse $s;
----
my $s = "abc";
say scalar reverse $s, "x" if 1;
----
my $s = "abc";
my $t = reverse $s;
----
my $s = "abc";
say reverse($s) . "x";
----
my $s = "abc";
say scalar reverse("") eq "" ? "empty" : "no";
----
say scalar reverse "", "";
----
my @a = ("", "");
say "[" . scalar reverse(@a) . "]";
----
my @a = (3, 1, 2);
say join(",", sort(@a));
say join(",", sort(@a), 9);
say join(",", sort({ $b <=> $a } @a));
say join(",", reverse(sort(@a)));
----
my @a = (3, 1, 2);
say sort(@a)[0];
----
my @a = (3, 1, 2);
say((sort(@a))[0]);
----
my @a = (3, 1, 2);
say join(",", sort (@a));
----
my @a = (3, 1, 2);
say join(",", sort (@a), 0);
----
my @a = (3, 1, 2);
sub f(@l) { return @l; }
say join(",", sort(f(@a)));
----
my @a = (3, 1, 2);
sub f(@l) { return @l; }
say join(",", sort(f @a));
----
my @a = (3, 1, 2);
sub f(@l) { return @l; }
say join(",", sort(f (@a)));
----
my @a = (3, 1, 2);
say join(",", sort(), 5);
----
my @a = (3, 1, 2);
say join(",", sort());
----
my @a = (3, 1, 2);
say join(",", sort(@a, 10, 9));
say join(",", sort((@a, 10, 9)));
say join(",", sort(sort(@a)));
----
my %h = (b => 1, a => 2);
say join(",", sort(keys %h));
for my $k (sort(keys %h)) { say $k; }
say join(",", map { $_ } sort(keys %h));
say join(",", grep { $_ } sort(keys(%h)));
my @k = sort(keys %h);
say "@k";
say scalar(@k);
----
my %h = (b => 1, a => 2);
say join(",", sort(values %h));
say join(",", sort { $h{$a} <=> $h{$b} } keys %h);
say join(",", sort({ $h{$a} <=> $h{$b} } keys %h));
----
my %h = (b => 1, a => 2);
sub f(@l) { return scalar(@l); }
say f(sort(keys %h));
say f(sort(keys %h), 1);
----
my %h = (b => 1, a => 2);
my ($first) = sort(keys %h);
say $first;
----
my %h = (b => 1, a => 2);
my $n = sort(keys %h);
----
my %h = (b => 1, a => 2);
say sort(keys %h) . "x";
----
my %h = (b => 1, a => 2);
say "x" . sort(keys %h);
----
my %h = (b => 1, a => 2);
say sort(keys %h) x 2;
----
my %h = (b => 1, a => 2);
say((sort(keys %h)) x 2);
----
my @a = (3, 1, 2);
say sort(@a) ? "t" : "f";
----
my @a = (3, 1, 2);
say sort(@a), "z";
----
my @a = (3, 1, 2);
say sort(@a) + 1;
----
my @a = (3, 1, 2);
say sort(@a) , 1;
----
my @a = (3, 1, 2);
say sort(@a) x 2;
----
my @a = (3, 1, 2);
print sort(@a);
print "\n";
----
my @a = (3, 1, 2);
say sort(@a) if 1;
----
my @a = (3, 1, 2);
say sort(@a) for 1 .. 2;
----
my @a = (3, 1, 2);
say sort(@a)
  , "x";
----
my @a = (3, 1, 2);
my @b = sort(@a) or die "e\n";
----
my @a = (3, 1, 2);
@a = sort(@a);
say "@a";
----
my @a = (3, undef, 2);
@a = sort({ ($a // 0) <=> ($b // 0) } @a);
say scalar(@a);
----
my @a = (3, 1, 2);
say join ",", sort(@a);
----
my @a = (3, 1, 2);
say join(",", sort(reverse @a));
say join(",", sort(reverse(@a)));
----
my @a = (3, 1, 2);
say join(",", sort(map { $_ * 2 } @a));
say join(",", sort(grep { $_ > 1 } @a));
----
my @a = (3, 1, 2);
say join(",", sort({ $a <=> $b } (@a)));
say join(",", sort({ $a <=> $b } @a), 0);
----
my @a = (3, 1, 2);
say join(",", sort({ $a <=> $b }));
----
my @a = (3, 1, 2);
say join(",", sort({ $a <=> $b } ));
----
my @a = (3, 1, 2);
say join(",", sort(+{ a => 1 }));
----
my @a = (3, 1, 2);
say join(",", sort({ a => 1 }));
----
my @a = (3, 1, 2);
say join(",", sort({ "a", 1 } @a));
----
my $by = sub { return $a <=> $b; };
my @a = (3, 1, 2);
say join(",", sort($by @a));
----
my @a = (3, 1, 2);
say join(",", sort(uc @a));
----
my @a = ("b", "a");
say join(",", sort(uc($a[0]), "B"));
----
my @a = ("b", "a");
say join(",", sort(lc "X", "B"));
----
my @a = ("b", "a");
say join(",", sort(scalar(@a), 1));
----
my @a = ("b", "a");
say join(",", sort(scalar @a, 1));
----
my @a = ("b", "a");
say join(",", sort("b", "a"));
say join(",", sort(1, 10, 9));
say join(",", sort(1 .. 11));
say join(",", sort(qw(z y x)));
----
my @a = ("b", "a");
say join(",", sort(true, false));
----
my @a = ("b", "a");
say join(",", sort(undef, "a"));
----
my @a = ("b", "a");
say join(",", sort(join("", @a), "aa"));
----
my @a = ("b", "a");
say join(",", sort(reverse "b", "a"));
----
my @a = ("b", "a");
say join(",", sort(sort @a));
----
my @a = ("b", "a");
say join(",", sort(defined $a[0], "x"));
----
my @a = ("b", "a");
say join(",", sort(length "abc", "x"));
----
my @a = ("b", "a");
say join(",", sort(-1, -2));
----
my @a = ("b", "a");
say join(",", sort(- 1, -2));
----
my @a = ("b", "a");
say join(",", sort(not 1));
----
my @a = ("b", "a");
say join(",", sort(sprintf("%s", "q"), "a"));
----
my @a = ("b", "a");
say join(",", sort(__LINE__, 0));
----
my @a = ("b", "a");
say join(",", sort(__FILE__ eq "x", 0));
----
my @a = ("b", "a");
say join(",", sort(ref [], "A"));
----
my @a = ("b", "a");
say join(",", sort(ucfirst "b", "A"));
----
my @a = ("b", "a");
say join(",", sort(quotemeta "b.", "A"));
----
my @a = ("b", "a");
say join(",", sort(scalar reverse("ab"), "a"));
----
my @a = ("b", "a");
say join(",", sort(chr 66, "A"));
----
my @a = ("b", "a");
say join(",", sort(ord "b", 97));
----
my @a = ("b", "a");
say join(",", sort(exists $a[0], 97));
----
my %h = (b => 1);
say join(",", sort(exists $h{b}, 97));
say join(",", sort(delete $h{b}, 97));
----
my @a = ("b", "a");
say join(",", sort(pop @a, "z"));
----
my @a = ("b", "a");
say join(",", sort(shift(@a), "z"));
----
my @a = ("b", "a");
say join(",", sort(substr("xb", 1), "a"));
----
my @a = ("b", "a");
say join(",", sort(index("xb", "b"), 0));
----
my @a = ("b", "a");
say join(",", sort(abs(-3), 0));
'''


def cases():
    return split('m', TEXT)
