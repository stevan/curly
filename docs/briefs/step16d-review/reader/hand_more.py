"""More by hand, after the first findings: scopes, lines, POD and the rest."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from split import split

TEXT = r'''
my $x = "outer";
{ my $x = 0 or die "v $x\n"; }
----
my $x = "outer";
sub f() { my $x = 0 or return "got $x"; return "no"; }
say f();
----
my $x = "outer";
{ my $x = 5 and say "v $x"; }
----
my $x = "outer";
for my $i (1 .. 2) { my $x = 0 or next; say "no"; }
say $x;
----
my $x = "outer";
{ my $x = 0 or warn "v $x\n"; }
----
my $x = 3;
{ my $x = $x - 3 or die "v $x\n"; }
----
my $x = 3;
{ my $y = 0 or die "v $y\n"; }
----
my @x = (1);
{ my $n = @x or die "none\n"; say $n; }
----
my $i = 0;
do { my $i = 5; say $i; } while ($i++ < 2);
----
my $i = 0;
do { $i++; my $i = 5; } while ($i < 2);
say $i;
----
my $i = 0;
do { say "b"; } until ($i++ or die "x\n");
----
my $i = 0;
do
{
  say "b";
}
until (warn "w\n");
----
my $i = 0;
do {
  say "b";
} until (
  warn "w");
----
my $i = 0;
do { say "b"; } until (warn "w");
----
my $i = 0; my $u;
do {
  $i++;
  say $u + 1 if $i > 1;
} while ($i < 3);
----
my $i = 0; my $u;
do {
  $i++;
} while ($i < 3 and
   $u + 1);
----
my $i = 0; my $u;
do
{
  $i++;
}
while ($u + 1);
----
my $i = 0; my $u;
do { $i++; }
while ($u + 1);
----
my $i = 0; my $u;
do { $i++; } while
  ($u + 1);
----
my $i = 0;
sub t() { warn "in t"; return 0; }
do {
  $i++;
} while (t());
----
my $i = 0;
do {
  $i++;
} while (__LINE__ > 100);
say __LINE__;
----
my $i = 0;
do {
  $i++;
} until (say(__LINE__));
----
my $i = 0;
if ($i) { say 1; }
elsif (warn "w") { say 2; }
----
my $i = 0;
$i++ while ($i < 3 or
  warn "w");
----
my @a = (1, 2, 3);
my $n = 0;
$n += $_ for 0 .. $#a;
say $n;
----
my @a = (1, 2, 3);
push @a, $_ for 0 .. $#a;
say "@a";
----
my @a = (1, 2, 3);
shift @a for 0 .. $#a;
say scalar(@a);
----
my @a = (1, 2, 3);
shift @a for @a;
----
my @a = (1, 2, 3);
my @b = map { shift @a } 0 .. $#a;
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { my @b = map { $_ } @a; push @a, scalar(@b); }
say "@a";
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { my @b = sort { $a <=> $b } @a; @a = (@b, 0); }
say "@a";
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { for my $x (@a) { push @a, 1 if $i > 5; } }
say "@a";
----
my @a = (1, 2, 3);
for my $x (@a) { for my $i (0 .. $#a) { $a[$i] = 0; last; } last; }
----
my @a = (1, 2, 3);
my @l = map { my $q = $_; for my $i (0 .. $#a) { $a[$i] = $q; } $q } 7, 8;
say "@a @l";
----
my @a = (1, 2, 3);
my @l = map { for my $i (0 .. $#a) { push @a, 1; } 1 } @a;
----
my @a = (1, 2, 3);
my @l = grep { for my $i (0 .. 0) { $a[0] = 9; } true } @a;
----
my @a = (3, 2, 1);
my @l = sort { for my $i (0 .. 0) { $a[0] = 9; } $a <=> $b } @a;
----
my @a = (1, 2, 3);
my $f = sub { for my $i (0 .. $#a) { push @a, $i; } return scalar(@a); };
say $f->();
say $f->();
----
my @a = (1, 2, 3);
my @s;
for my $x (@a) { push @s, sub { return $x; }; }
for my $i (0 .. $#a) { push @a, 4; }
----
my @a = (1, 2, 3);
my @s;
for my $i (0 .. $#a) { push @s, sub { return $i; }; }
for my $x (@a) { push @s, sub { return $x; }; }
say join(",", map { $_->() } @s);
push @a, 1;
----
my $n = 3;
my @s;
for my $i (1 .. $n) { push @s, sub { $n = 0; return $i; }; }
say join(",", map { $_->() } @s), " $n";
----
my $n = 3;
my @s;
for my $i (1 .. $n, 9) { push @s, sub { return $i; }; }
----
my $n = 3;
my @s;
for my $i (1 .. $n) { push @s, \$n; $n++; }
say scalar(@s), " $n";
----
my $n = 3;
my $r = \$n;
for my $i (1 .. $n) { $r->$*++; }
say $n;
----
my $n = 3;
my $r = \$n;
for my $i (1 .. $r->$*) { $n = 0; say $i; }
----
my $n = 3;
my $r = \$n;
for my $i (1 .. ${$r}) { $r->$* = 0; say $i; }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { say "$a[$i] $#a"; pop @a; }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { say defined $a[$i] ? "d" : "u"; undef @a; }
----
my @a = (1, 2, 3);
for my $i (0 .. $#a) { delete_all(); say scalar(@a); }
sub delete_all() { @a = (); return; }
----
my @m = ([1, 2], [3, 4]);
for my $i (0 .. $#m) { for my $j (0 .. $#{$m[$i]}) { $m[$i][$j] *= 2; push $m[$i]->@*, 0 if $j == 0; } }
say join("|", map { "$_->@*" } @m);
----
my @m = ([1, 2], [3, 4]);
for my $i (0 .. $#m) { for my $j (0 .. $m[$i]->$#*) { $m[$j][$i] = $m[$i][$j]; } }
say join("|", map { "$_->@*" } @m);
----
my @m = ([1, 2], [3, 4]);
for my $i (0 .. $#m) { $m[$i] = [0]; $#m = 0; }
say scalar(@m);
----
my @a = (5, 3, 8, 1);
for my $i (1 .. $#a) { my $v = $a[$i]; my $j = $i - 1; while ($j >= 0 and $a[$j] > $v) { $a[$j + 1] = $a[$j]; $j--; } $a[$j + 1] = $v; }
say "@a";
----
my %h = (a => 1);
for my $i (1 .. keys %h) { for my $v (values %h) { say $v; } $h{b} = 2; }
say scalar(%h);
----
my %h = (a => 1);
for my $v (values %h) { for my $i (1 .. keys %h) { $h{b} = 2; } }
----
say "\Uabc\E" . "def" . "\LGHI";
say "\Q.\E" x 2;
say "a\Ub\Ec\Ld\Ee\Qf.\Eg";
say "\U\E\L\E\Q\E.";
----
say "\Ua\LB\EC";
----
say "\LA\UB\Ec";
----
say "\Qa\Ub.\Ec.";
----
say "\U\Qa.b\E\Ec";
----
say "\Q\Ua.b\E\Ec";
----
say "\u\Uab";
say "\l\LAB";
say "\u\LAB cd";
say "\l\Uab cd";
say "\u\Qa.b";
----
say "\uab\E";
----
say "\u\E";
----
say "\U\u\Eab";
----
say "\u\Uab\Ecd\Lef";
----
say "\Uab\u";
----
say "\Uab\ucd";
----
say "\Uab\E\ucd";
say "\Lab\E\ucd\Uef\E";
----
say "\Ua\tb\E";
say "\Ua\x62c\E";
say "\Ua\x{62}c\E";
say "\Ua\142c\E";
say "\Ua\N{U+62}c\E";
say "\Qa\tb\E";
say "\Q\x2e\E";
----
my $x = "a.b";
say "\Q$x\E" eq quotemeta($x) ? "y" : "n";
say "\U$x\E" eq uc($x) ? "y" : "n";
say "\L\u$x\E" eq ucfirst(lc($x)) ? "y" : "n";
say "\u\L$x\E!" ;
----
my @a = ("x.y", "Z");
say "\Q@a\E";
say "\U@a[0, 1]\E";
say "\L$a[1]$a[0]\E";
say "\u$a[0]";
say "\l$a[1]$a[0]";
say "\u@a";
----
my @a = ();
say "\u@a!";
say "\U@a\E!";
----
my $u;
say "\U$u\E";
----
my $u;
say "\u$u";
----
my $u; my $x = "a";
say "\u$x$u";
----
my $u; my $x = "a";
say "\U$x\E$u";
----
my $r = [1];
say "\U$r\E";
----
my $n = 1.50;
say "\U$n\E \Q$n\E \u$n";
----
my $n = 1e20;
say "\Q$n\E \U$n\E";
----
my $n = -5;
say "\Q$n\E";
----
my $t = true; my $f = false;
say "\Q$t$f\E|\U$f\E|";
----
print <<END;
\Uabc\E def \Qg.h\E
\uxyz
END
----
print <<"END";
\Uabc
END
print "next\n";
----
print <<'END';
\Uabc\E
END
----
print <<~END;
    \Uabc\E
      \LDEF
    END
----
say qq{\Uabc\E};
say qq(\Q(.)\E);
say qq[\u[x]];
----
say q{\Uabc\E};
say '\Uabc\E';
----
my %h = ("\Uab\E" => 1, "\Qc.d\E", 2);
say join(",", sort keys %h);
----
my %h = (AB => 1);
say $h{"\Uab\E"};
say "$h{AB}\U$h{AB}x\E";
----
say length("\Q\x{0}\E");
say "\Q \E" eq "\\ " ? "y" : "n";
say "\Q\\\E" eq "\\\\" ? "y" : "n";
say "\Q\E" eq "" ? "y" : "n";
----
say "\Q\t\E" eq "\\\t" ? "y" : "n";
say "\Qé\E" eq "é" ? "y" : "n";
say "\Q\x{e9}\E" eq "\x{e9}" ? "y" : "n";
say "\Q\x{a0}\E" eq "\\\x{a0}" ? "y" : "n";
say "\Q\x{d7}\E" eq "\\\x{d7}" ? "y" : "n";
say "\Q\x{2000}\E" eq "\\\x{2000}" ? "y" : "n";
----
say "\U\x{df}\E", "\u\x{df}x", "\L\x{130}\E", "\l\x{130}x";
----
say "\Uǆ\E\uǆ\LǄ\E\lǄ";
----
my $s = "abc";
say uc $s . "d";
say uc($s) . "d";
say lc "ABC" x 2;
say ucfirst lc "ABC";
say quotemeta uc "a.b";
say lcfirst(uc "abc") . "!";
say uc "a" lt "b" ? "y" : "n";
say uc("a") lt "b" ? "y" : "n";
say join(",", uc "a", lc "B");
say join(",", quotemeta "a.", "b.");
----
say quotemeta "a" x 2, "z";
----
say quotemeta "a." . "b.";
----
say quotemeta("a." . "b.");
say quotemeta "a." eq "a\\." ? "y" : "n";
----
say quotemeta;
----
say quotemeta();
----
say quotemeta "a", "b";
----
say quotemeta("a", "b");
----
for ("a.b") { say quotemeta $_; say quotemeta($_); }
----
for ("a.b") { say quotemeta; }
----
for ("a.b") { say uc; }
----
my @a = ("a.", "b");
say quotemeta @a;
----
my @a = ("a.", "b");
say quotemeta $a[0];
say quotemeta $a[0] . $a[1];
say quotemeta -5;
say quotemeta - 5;
----
say quotemeta 1.0;
say quotemeta 1e3;
say quotemeta 0x10;
say quotemeta true;
say quotemeta false;
say "[" . quotemeta("") . "]";
----
say quotemeta undef;
----
say quotemeta [];
----
say __FILE__ =~ "x";
----
my $f = __FILE__;
say length($f) > 3 ? "long" : "short";
say substr(__FILE__, -3);
say __FILE__ eq $f ? "y" : "n";
say "in @{[ 5 ]}";
----
my $f = __FILE__;
say substr($f, -3), ":", __LINE__;
warn "at ", substr(__FILE__, -3), " line ", __LINE__, ".\n";
----
say __FILE__ . ":" . __LINE__ eq "x" ? "y" : "n";
----
say __LINE__ - 1;
say __LINE__ -1;
----
say __LINE__ x 2;
say __LINE__ . __LINE__;
say __LINE__ < 5 ? "lt" : "ge";
say __LINE__ <=> 2;
----
say __LINE__ [0];
----
say __LINE__->[0];
----
say __LINE__ = 5;
----
say __LINE__++;
----
my @a = (10, 20, 30, 40);
say $a[__LINE__];
say $a[ __LINE__ - 1 ];
----
my %h = (2 => "two", __LINE__ => "L");
say $h{2};
----
my %h = (__LINE__ => "L");
say join(",", keys %h);
----
my %h = (__LINE__, "L");
say join(",", keys %h);
----
my %h = (__FILE__ => "L");
say join(",", keys %h);
----
my %h = (__LINE__
  => "L");
say join(",", keys %h);
----
my %h = (k => 1);
say $h{__FILE__} // "u";
say $h{__LINE__} // "u";
----
say "a" .
  __LINE__ .
  "b" . __LINE__;
----
my $x = sub { return __LINE__; }->();
say $x;
----
my $x = sub {
  return (__LINE__,
    __LINE__); };
say join(",", $x->());
----
say __LINE__, "
", __LINE__;
----
say <<A . __LINE__ . <<B;
a
A
b
B
----
my @l = (<<A, __LINE__);
a
b
A
say @l;
say __LINE__;
----
say sprintf("%d
%d", __LINE__, __LINE__);
----
say "x"; # c
# c
say __LINE__;

say __LINE__;
----
say 1;

=pod

=cut

say __LINE__;
die "here";
----
say 1;
=pod
=cut
die "here";
=pod
----
say 1;
=head1 A

=head1 B

=cut

=cut

say 2;
=cut
say 3;
----
say 1;
=pod

__END__

=cut
say 2;
----
say 1;
=pod
"unterminated
'also
<<X
=cut
say 2;
----
sub f() {
    return 1;

=pod

=cut

}
say f();
----
my $x = 1;
if ($x) {

=pod

=cut

    say "in";
}

=pod

=cut

else {
    say "no";
}
----
my @a = (1,
    2,

=pod

=cut

    3);
----
my $h = {

=pod

=cut

    a => 1 };
----
my $x = 1;
{
=pod
=cut
    say $x;
}
----
my $x = 1;
{
    say $x;
=pod
=cut
}
say "end";
----
my $x = sub {
    return 5;
=pod
=cut
};
say $x->();
----
my $x = sub {
=pod
=cut
    return 5;
};
say $x->();
----
my @l = map {
=pod
=cut
    $_ * 2 } 1, 2;
say "@l";
----
my @l = map { my $q = $_;
=pod
=cut
    $q * 2 } 1, 2;
say "@l";
----
try {
=pod
=cut
    die "x\n";
}
=pod
=cut
catch ($e) {
=pod
=cut
    print $e;
}
----
for my $i (1 .. 2)
=pod
=cut
{ say $i; }
----
for my $i
=pod
=cut
(1 .. 2) { say $i; }
----
sub f()
=pod
=cut
{ return 1; }
say f();
----
sub
=pod
=cut
f() { return 1; }
----
while (0) { }
=pod
=cut
say "ok";
----
L:
=pod
=cut
for my $i (1) { next L; }
say "ok";
----
my $i = 0;
do {
=pod
=cut
  $i++;
} while ($i < 2);
say $i;
----
my $i = 0;
do {
  $i++;
=pod
=cut
} while ($i < 2);
say $i;
----
my $i = 0;
do { $i++; } while ($i < 2)
=pod
=cut
;
say $i;
----
use experimental 'class';
----
say 1;
=pod
----
say 1;
=pod
=cut
----
say 1
=pod
=cut
;
'''


def cases():
    return split('h', TEXT)
