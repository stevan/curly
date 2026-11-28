"""D254 to D257 and D261 by hand."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from split import split

TEXT = r'''
my $s = "abcd";
substr($s, 1, 2, "XYZ");
say $s;
substr($s, 0, 0, "<");
say $s;
substr($s, length($s), 0, ">");
say $s;
substr($s, -1, 1, "");
say $s;
substr($s, 2, 100, "!");
say $s;
substr($s, -2, -1, "?");
say $s;
----
my $s = "abcd";
substr($s, 5, 1, "x");
say $s;
----
my $s = "abcd";
substr($s, -5, 1, "x");
say $s;
----
my $s = "abcd";
substr($s, -5, 2, "x");
say $s;
----
my $s = "abcd";
substr($s, -6, 3, "x");
say $s;
----
my $s = "abcd";
substr($s, -6, 1, "x");
say $s;
----
my $s = "abcd";
substr($s, 2, -3, "x");
say $s;
----
my $s = "abcd";
substr($s, 4, -1, "x");
say $s;
----
my $s = "abcd";
substr($s, 1.9, 1.9, "x");
say $s;
----
my $s = "abcd";
substr($s, "1", "2", 5);
say $s;
----
my $s = "abcd";
my $u;
substr($s, 1, 1, $u);
say $s;
----
my $s = "abcd";
my $u;
substr($s, $u, 1, "x");
say $s;
----
my $s = "abcd";
my $u;
substr($s, 0, $u, "x");
say $s;
----
my $s;
substr($s, 0, 0, "x");
say $s;
----
my $s = 12345;
substr($s, 1, 2, "x");
say $s;
----
my $s = 1.5;
substr($s, 1, 1, ",");
say $s;
----
my $s = true;
substr($s, 0, 1, "yes");
say $s;
----
my $s = [1];
substr($s, 0, 1, "yes");
----
my $s = "héllo wörld";
substr($s, 1, 1, "e");
substr($s, -4, 1, "ö" x 2);
say $s;
say length $s;
----
my $s = "abc";
substr($s, 1, 1, "é");
say length $s;
----
my $s = "abc";
substr($s, 1, 1, $s);
say $s;
----
my $s = "abc";
substr($s, 1, 1, substr($s, 0, 1));
say $s;
----
my $s = "abc";
my $n = 0;
sub f() { $n++; return 1; }
substr($s, f(), f(), "x" . f());
say "$s $n";
----
my $s = "abc";
substr($s, ($s = "wxyz") ? 1 : 0, 1, "-");
say $s;
----
my $s = "abc";
substr($s, 1, 1, ($s = "wxyz"));
say $s;
----
my $s = "abc";
substr($s, 1, 1, "x") if length($s) > 2;
say $s;
----
my $s = "abc";
substr($s, 0, 1, "x") for 1 .. 2;
say $s;
----
my @a = ("abc");
substr($a[0], 1, 1, "x");
----
my $r = \"abc";
----
my $s = "abc";
my $r = \$s;
substr($r->$*, 1, 1, "x");
----
my $s = "abc";
my $r = \$s;
substr($s, 1, 1, "x");
say $r->$*;
----
my $s = "abc";
my $old = substr($s, 1, 1, "x");
----
my $s = "abc";
say substr($s, 1, 1, "x");
----
my $s = "abc";
substr($s, 1, 1) = "x";
----
my $s = "abc";
substr($s, 1, 1, "x", 5);
----
for my $s ("abc") { substr($s, 1, 1, "x"); }
----
for ("abc") { substr($_, 1, 1, "x"); }
----
sub f($s) { substr($s, 0, 1, "X"); return $s; }
my $v = "abc";
say f($v), $v;
----
sub f($s) { substr($s, 0, 1, "X") }
say f("abc");
----
sub f($s) { substr($s, 0, 1, "X"); }
my @l = (f("abc"));
say scalar(@l);
----
my $s = "abc";
substr($s, 0, 1, "X"), say "x";
----
my $s = "abc";
substr($s, 3, 0, "d");
substr($s, 3, 5, "D");
substr($s, 4, 0, "e");
say $s;
----
my $s = "abc";
substr($s, 4, 0, "e");
----
my $s = "";
substr($s, 0, 0, "e");
substr($s, 0, -1, "f");
say $s;
----
my $s = "";
substr($s, -1, 0, "e");
say $s;
----
my $s = "abc";
substr($s, 0, -5, "e");
say $s;
----
my $s = "abc";
substr($s, 1, -5, "e");
say $s;
----
my $s = "abc";
substr($s, -1, -5, "e");
say $s;
----
my $s = "abc";
substr($s, 9223372036854775807, 1, "e");
----
my $s = "abc";
substr($s, 1, 9223372036854775807, "e");
say $s;
----
my $s = "abc";
substr($s, 1, 1e30, "e");
say $s;
----
my $s = "abc";
substr($s, -9223372036854775808, 1, "e");
----
my $s = "abc";
substr($s, 1, -9223372036854775808, "e");
say $s;
----
say __LINE__;
say __FILE__ eq "x" ? "x" : "path";
say __LINE__ + 1;
say "line " . __LINE__;
say "line @{[ 1 ]}";
----
say __LINE__, " ",
  __LINE__, " ",
  __LINE__;
----
my $s = "a
b"; say __LINE__;
say __LINE__;
----
my $s = <<END; say __LINE__;
one
two
END
say __LINE__;
----
my $s = <<END . __LINE__;
one
END
print $s, "\n";
----
say <<END, __LINE__;
one
two
END
----
say
   __LINE__
   ;
----
say(
   __LINE__ +
   __LINE__
);
----
my %h = (__LINE__ => 1, __FILE__ => 2);
say join(",", sort keys %h);
----
my %h = (__LINE__, 1);
say join(",", sort keys %h);
----
my %h = (a => 1);
say $h{__LINE__} // "none";
----
my %h = (2 => "two");
say $h{+__LINE__} // "none";
----
say __LINE__ . "";
say __LINE__ x 2;
say __LINE__ == 3 ? "y" : "n";
say -__LINE__;
say __LINE__ ** 2;
----
say __LINE__();
----
say __LINE__ ();
----
say __FILE__();
----
say "__LINE__ __FILE__";
----
say length(__FILE__) > 0 ? "y" : "n";
----
sub f($n = __LINE__) { return $n; }
say f();
----
sub f() { return __LINE__; }
say f();
----
my @a = (__LINE__,
  __LINE__);
say "@a";
----
die "at " . __LINE__ . "\n";
----
die __FILE__ eq "" ? "a" : "b";
----
warn "w ", __LINE__;
----
warn __LINE__;
----
die __LINE__;
----
die
  "x\n";
----
warn "a\n",
  __LINE__, "\n";
----
say __PACKAGE__;
----
say __SUB__;
----
say __line__;
----
say __END__;
----
my $x = __LINE__
;
say $x;
----
my $x = 1; # comment __LINE__
say __LINE__; =pod
----
say 1;

=pod

say 2;

=cut

say 3;
----
say 1;
=head1 NAME
say 2;
=cut
say 3;
----
say 1;
=cut
say 2;
=cut
say 3;
----
say 1;
=pod
say 2;
----
say 1;
=pod
say 2;
=cutx
say 3;
=cut x
say 4;
----
say 1;
=pod
say 2;
 =cut
say 3;
----
say 1;
=begin comment
say 2;
=end comment
say 3;
=cut
say 4;
----
say 1;
=for comment text
say 2;
=cut
say 3;
----
say 1;
=1
say 2;
----
say 1;
=_x
say 2;
=cut
say 3;
----
say 1;
= pod
say 2;
----
say 1;
=Pod
say 2;
=CUT
say 3;
=cut
say 4;
----
say 1;
=pod=cut
say 2;
=cut
say 3;
----
my $x
=pod
=cut
= 5;
say $x;
----
my $x =
=pod

=cut
5;
say $x;
----
my $x = 5
;
=pod
=cut
say $x;
----
sub f() {
=pod

doc

=cut
  return 5;
}
say f();
----
sub f() {
  my $x = 1;
=pod
=cut
  return $x;
}
say f();
----
if (1) {
=pod
=cut
  say "in";
}
=pod
=cut
else { say "no"; }
----
if (1) {
  say "in";
}
=pod
=cut
say "after";
----
for my $i (1 .. 2) {
=pod
=cut
}
say "ok";
----
my @a = (1,
=pod
=cut
2);
say "@a";
----
my $s = "a
=pod
b";
say $s;
----
my $s = <<END;
a
=pod
b
=cut
END
print $s;
----
say 1; =pod
say 2;
----
#raw
=pod

=cut
use v5.42;
say "ok";
----
#raw
=pod
use v5.42;
=cut
say "ok";
----
#raw
use v5.42;
=pod

=cut
say __LINE__;
die "here";
----
#raw
use v5.42;
=pod
# line 200 "x"
=cut
die "here";
----
#raw
use v5.42;
=pod
  # line 200
=cut
die "here";
----
#raw
use v5.42;
=pod
#line 200
=cut
die "here";
----
#raw
use v5.42;
=pod
x # line 200
=cut
die "here";
----
#raw
use v5.42;
=pod
# line 200
----
#raw
use v5.42;
say 1;
__END__
# line 200
say 2;
----
#raw
use v5.42;
say 1;
__END__
----
#raw
use v5.42;
say 1;
__END__ say 2;
say 3;
----
#raw
use v5.42;
say 1;
__DATA__
say 2;
----
#raw
use v5.42;
say 1; __END__
say 2;
----
#raw
use v5.42;
say 1
__END__
say 2;
----
#raw
use v5.42;
say 1,
__END__
say 2;
----
#raw
use v5.42;
if (1) { say 1;
__END__
}
----
#raw
use v5.42;
sub f() { return 1;
__END__
}
----
#raw
use v5.42;
say "a
__END__
b";
----
#raw
use v5.42;
say <<X;
__END__
X
say 2;
----
#raw
use v5.42;
say 1;
  __END__
say 2;
----
#raw
use v5.42;
say 1;
__END__;
say 2;
----
#raw
use v5.42;
say 1;
__END__x
----
#raw
use v5.42;
my %h = (__END__ => 1);
say join(",", keys %h);
----
#raw
use v5.42;
my %h = (a => 1);
say $h{__END__} // "none";
----
#raw
use v5.42;
say 1;
=pod
__END__
=cut
say 2;
----
#raw
use v5.42;
say 1;
__END__
=pod
----
#raw
use v5.42;
say 1;
__END__
"unterminated
----
#raw
use v5.42;
say 1;
__END__
é ÿ not checked
----
#raw
use v5.42;
say 1;
=pod
é
=cut
say 2;
----
#raw
use v5.42;
say 1;
__DATA__
é
----
#raw
use v5.42;
say 1;
__END__
----
my $x = "abc"; my $y = "Def";
say "\U$x\E$y";
say "\u\L$y";
say "\L\u$y";
say "\Q$x.$y\E.";
say "\Uabc";
say "a\Ubc\Ede";
say "\LABC\E\Uabc\E";
say "\u$x \u$y";
say "\l$y";
say "\Ué\E \LÉ\E";
----
my $x = "abc";
say "\Uab\Lcd\Eef";
----
my $x = "abc";
say "\Uab\Qc.d\Eef";
----
my $x = "abc";
say "\Uab\E\E";
----
my $x = "abc";
say "ab\E";
----
my $x = "abc";
say "\U\E";
say "\U";
say "\Q";
say "\u";
say "\l";
say "a\u";
----
my $x = "abc";
say "\U\uab";
say "\U\lAB";
say "\L\uab";
say "\L\lAB";
say "\Q\ua.b";
----
my $x = "abc";
say "\Ua\ub";
----
my $x = "abc";
say "\uab\ucd";
say "\u\uab";
say "\l\uab";
say "\u\lAB";
say "x \uab";
say "\u $x";
say "\u\n$x";
----
my $x = "abc";
say "\u\Uabc\Edef";
----
my $x = "abc"; my $e = "";
say "\u${e}d";
say "\u$e$x";
say "\u$e";
say "\l$e" . "X";
----
my @a = ("ab", "cd");
say "\U@a\E";
say "\u@a";
say "\Q@a\E";
say "\U$a[0]\E$a[1]";
say "\u$a[1]";
say "\U$#a\E";
----
my $r = { k => "v w" };
say "\U$r->{k}\E";
say "\u$r->{k}";
say "\Q$r->{k}\E";
----
my $x = "a.b*c";
say "\Q$x\E";
say "\Q$x";
say "\Q a b\E";
say "\Q\n\t\E";
say "\Qé ü\E";
say "\Q\x{2028}\x{ad}\x{3000}\E";
say "\Q$x\E$x";
say "\Qa\\b\E";
say "\Q\$x \@y\E";
say "\Q\"\E";
----
say "\Q\\E";
----
say "\Qa\\Eb\E";
----
say "\Q\U";
----
say "\Ua\\Eb";
----
say "\U\$x\E";
say "\U\x41\x{e9}\E";
say "\L\x41\x{c9}\E";
say "\U\tx\E";
say "\L\N{U+C9}\E";
say "\u\x{e9}a";
----
say "\Uß\E";
say "\uß";
say "\Lİ\E";
say "\uǆ";
say "\Uǆ\E";
say "\LΣ\E";
say "\LΑΣ\E";
say "\Uﬁ\E";
say "\uﬁ";
say "\uŉ";
----
say uc "ß";
say ucfirst "ßa";
say lc "İ";
say length lc "İ";
say ucfirst "ǆa";
say uc "ǆa";
say lc "ΑΣ";
say lc "ΑΣ ΑΣΑ";
say uc "ﬁ";
say ucfirst "ﬁx";
say lcfirst "ǅX";
say lcfirst "İX";
say uc "ŉ";
say uc "ᾳ";
say ucfirst "ᾳ";
say lc "ᾼ";
say uc "ᾼ";
say uc "\x{345}";
say uc "a\x{345}";
say uc "\x{345}a\x{345}";
----
say uc "\x{345}\x{345}";
----
say ucfirst "\x{345}\x{345}";
----
say uc "\x{345}\x{301}\x{345}";
----
say uc "ᾳ\x{345}";
----
say uc "\x{1f80}\x{345}";
----
say "\U\x{345}\x{345}\E";
----
my $a1 = "\x{345}";
say "\U$a1$a1\E";
----
my $a1 = "\x{345}";
say uc($a1 . $a1);
----
my $a1 = "\x{345}";
say uc($a1) . uc($a1);
----
my $a1 = "\x{345}";
say "\U$a1\E\U$a1\E";
----
say uc "\x{3b1}\x{345}\x{345}";
----
say uc "\x{399}\x{345}";
----
say uc "\x{345}\x{399}";
----
say lc "\x{345}\x{345}";
say ucfirst "\x{345}x\x{345}";
----
say uc "\x{1fb3}\x{1fb3}";
----
say uc "\x{1fb3}\x{345}";
----
say uc "\x{1f80}\x{1f80}";
----
say uc "\x{1fc3}\x{1ff3}";
----
say uc "\x{345}\x{300}";
----
say uc "\x{300}\x{345}";
----
say uc "\x{345}\x{315}\x{345}";
----
say uc "\x{345}\x{316}\x{345}";
----
say uc "\x{345}\x{361}\x{345}";
----
say uc "\x{345}\x{1d165}\x{345}";
----
say uc "a\x{345}\x{300}";
----
say uc "\x{3b1}\x{300}\x{345}";
----
say uc "\x{3b1}\x{345}\x{300}";
----
say uc "\x{1fb3}\x{300}";
----
say uc "\x{1fb3}\x{301}\x{1fb3}";
----
say uc "\x{1fb7}\x{301}";
----
say uc "\x{1f80}\x{300}";
----
say uc "\x{1f80}\x{301}\x{345}";
----
say uc "\x{390}\x{345}";
----
say uc "\x{3b1}\x{345}\x{3b1}\x{345}";
----
say uc "\x{345}\x{3b1}\x{345}";
----
say uc "\x{345}\x{20dd}\x{345}";
----
say uc "\x{345} \x{345}";
----
say quotemeta "a.b";
say quotemeta "é";
say quotemeta "\x{2028}";
say quotemeta "a b\tc\n";
say quotemeta "_09azAZ";
say quotemeta "";
say quotemeta 1.5;
say quotemeta "\x{ad}\x{34f}\x{115f}\x{3164}\x{ffa0}\x{e0001}";
say quotemeta "\x{7f}\x{80}\x{a0}\x{aa}\x{b5}\x{ff}";
say length quotemeta "\x{0}";
----
my $u;
say quotemeta $u;
----
say quotemeta [1];
----
say quotemeta "a" . "b.";
say quotemeta("a") . "b.";
say quotemeta "a", "b";
----
say quotemeta;
----
say uc "straße";
say lc "STRASSE ÀÉ";
say ucfirst "élan";
say lcfirst "Élan";
say uc "\x{10428}";
say lc "\x{10400}";
say uc "ա";
say uc "ﬃ";
say lc "ẞ";
say uc "ı";
say lc "I";
say uc "ǰ";
say ucfirst "ǳ";
say uc "ǳ";
say ucfirst "ǉ";
say lcfirst "Ǉ";
say lcfirst "ǈ";
say uc "ΐ";
say uc "ﬓ";
say ucfirst "ﬓ";
----
say uc "\x{df}" eq "SS" ? "y" : "n";
say length uc "\x{fb03}";
say length uc "\x{390}";
say length ucfirst "\x{390}";
say length lc "\x{130}";
say length lcfirst "\x{130}";
----
die "a\n" . "";
----
die "a" . "\n" x 1;
----
die "a" .
  "\n";
----
die "a\n" .
  "";
----
my $x = "v";
die sprintf("%s\n",
  $x);
----
my $x = "v";
die sprintf("a\n%s",
  "");
----
die "a\n",
  "";
----
die "a\n",
  "b";
----
die "a",
  "b\n";
----
die "a\x0a" .
  "";
----
die "a",
  "\x0a";
----
die "a",
  "\x{a}";
----
die "a",
  "\012";
----
die "a",
  "\cJ";
----
die "a",
  "\N{U+0A}";
----
die "a",
  "\o{12}";
----
die "a",
  "\n\E";
----
die "a",
  "\Ub\n";
----
die "a",
  "\Ub\n\E";
----
die "a",
  "\Q\n";
----
die "a",
  "\Qb\E\n";
----
die "a",
  "\u\n";
----
die "a",
  "\L\n\E";
----
die "a",
  'b\n';
----
die "a",
  q(b
);
----
die "a",
  qq(b\n);
----
die "a",
  "b
";
----
die <<END;
a
END
----
die <<END,
a
END
  "b";
----
die "a",
  <<END;
b
END
----
die "a",
  <<~END;
    b
    END
----
die "a",
  <<'END';
b\n
END
----
die "a" .
  <<END . "c";
b
END
----
die "a" .
  ("b" . "\n");
----
die "a" .
  ("b\n" . "c");
----
die "a" . "\n"
  x 0;
----
die(("a" .
  "\n") x 0);
----
die "a" .
  "\n" . "";
----
my $e = "";
die "a" .
  "\n" . $e;
----
my $e = "";
die "a" .
  "\n$e";
----
my $e = "";
die "a" .
  "$e\n";
----
my $e = "x\n";
die "a" .
  "$e";
----
my $e = "x\n";
die "a" .
  $e;
----
my $e = "";
die "a\n" .
  $e;
----
die "a" .
  "\n" if 1;
----
die +("a" .
  "\n");
----
die "a" . ("\n" .
  "b");
----
die "a" . sprintf("%s\n",
  "b");
----
die sprintf("%s\n",
  "b") . "c";
----
die sprintf("%s\n" .
  "c", "b");
----
die sprintf("%s\n%%",
  "b");
----
die sprintf("%s%%\n",
  "b");
----
die sprintf("%s\n",
  "b"), "c";
----
die sprintf('%s\n',
  "b");
----
die sprintf("%c",
  10);
----
die sprintf("%s",
  "b\n");
----
die sprintf("\n");
----
die sprintf("x\n"
  );
----
die sprintf("%-3s|\n",
  "b");
----
die sprintf("%s\n\n",
  "b");
----
die sprintf("%s\n ",
  "b");
----
die sprintf("%s\n",
  "b") if 1;
----
die "a" . "\n"
  if 1;
----
die "a\n"
  if 1;
----
die "a"
  if 1;
----
warn "a" .
  "\n";
say "after";
----
warn sprintf("%d\n",
  5);
----
warn "a" . "\n" x 0,
  "";
----
my @l = ("a", "b\n");
die join("",
  @l);
----
my @l = ("a\n");
die
  @l;
----
my $m = "a\n";
die
  $m;
----
die "a" .
  "b";
----
die
  "a" . "b";
----
my $c = 1;
die $c ? "a\n" : "b\n",
  "";
----
my $c = 1;
die "x",
  $c ? "a\n" : "b\n";
----
my $c = 1;
die "x",
  ("a\n");
----
my $c = 1;
die "x",
  "a\n" x 2;
----
my $c = 1;
die "x",
  "a\n" x $c;
----
my $c = 0;
die "x",
  ("a" . "\n") x $c;
----
die "x",
  uc "a\n";
----
die "x",
  lc("a\n");
----
die "x", "\n" .
  "";
----
die "x" . "\n" ,
  ;
----
die("x" . "\n"
  ,);
----
die "a
b";
----
die "a
";
----
my $i = 0;
while (die "x" . "\n") { }
----
my $i = 0;
while ($i++ < 1) {
  die "x" .
   "y\n" }
----
my $i = 0;
$i++ or
  die "x" . "\n";
----
my $i = 0;
$i++ or
  die "x\n" . "y";
'''


def cases():
    return split('s', TEXT)
