# the case escapes in double quotes, qq and a heredoc (D256).
use v5.42;
my $x = "fOO";
say "\U$x\E-\L$x\E-\u$x-\l$x-\u\L$x\E-\L\u$x\E-\Qa.b\E";
my $y = "fOO bar";
say "a\Uxy$y z\Ew";
my $e = "";
say "\u${e}d";
say "\Ua${e}b\E";
say "\uab\Ucd";
say "\u\lABC";
say "\l\uabc";
say "\U\uabc\E";
say "x\L\uABC\E-\uyz";
say "a\u";
say "\Q\E|";
my @a = ("ab", "cd");
say "\u@a";
say "\U$a[0]\E$a[1]";
say qq{\Ux\E}, qq(\u$x);
print <<"END";
\Uhere $x\E done \Q[.]\E
END
say "\Q$y\E";
say quotemeta("a.b"), " ", quotemeta("-_x1 ");
