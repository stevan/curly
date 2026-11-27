# kind: same
# Matches by hand, each shape the proposal names (step 19; D226 to D237).
use v5.42;
use utf8;
use open ":std", ":encoding(UTF-8)";
my $line = "key = value";
my ($k, $v) = $line =~ /^(\w+)\s*=\s*(.*)$/;
say "$k|$v";
my @none = ("abc" =~ /(x)/);
say scalar(@none);
my @one = ("abc" =~ /b/);
say "@one";
my @gap = ("ab" =~ /(a)(x)?/);
say scalar(@gap), defined $gap[1] ? "d" : "u";
say "a" !~ /b/ ? "not" : "is";
my @not = ("a" !~ /a/);
say scalar(@not), "[@not]";
say "[", "a" =~ /b/, "]";
say "٣" =~ /^\d$/ ? "digit" : "no";
say "Ⅳ" =~ /^\w$/ ? "word" : "no", "Ⅳ" =~ /\d/ ? "digit" : "no";
say "\x{a0}" =~ /\s/ ? "blank" : "no", "\x{200b}" =~ /\s/ ? "blank" : "no";
say "é" =~ /^.$/ ? "one" : "two", "e\x{301}" =~ /^.$/ ? "one" : "two";
say "a\n" =~ /a$/ ? 1 : 0, "a\n\n" =~ /a$/ ? 1 : 0, "a\n" =~ /a\z/ ? 1 : 0, "a\n" =~ /a\Z/ ? 1 : 0;
say "a\nb" =~ /^b/ ? 1 : 0, "a\nb" =~ /^b/m ? 1 : 0, "a\n" =~ /\n^/m ? 1 : 0;
say "a\nb" =~ /a.b/ ? 1 : 0, "a\nb" =~ /a.b/s ? 1 : 0;
say "ABC" =~ /b/i ? 1 : 0, "abc" =~ /[A-C]{3}/i ? 1 : 0, "abab" =~ /^(AB)\1$/i ? 1 : 0;
say join "|", "aab" =~ /a*/g;
say join "|", "ab" =~ /x*|a/g;
my @e = ("abc" =~ /x*/g);
say scalar(@e);
say join ",", map { $_ // "u" } "ab" =~ /(a)|(b)/g;
say join ",", "a1b22c333" =~ /(\d+)/g;
say join ",", "k1=v1;k2=v2" =~ /(\w+)=(\w+)/g;
my @l = ("a\n\nb" =~ /^/mg);
say scalar(@l);
@l = ("a\n" =~ /$/g);
say scalar(@l);
say "x{y}" =~ m{\{y\}} ? 1 : 0, "aa" =~ m{a{2}} ? 1 : 0, "a)" =~ m(a\)) ? 1 : 0, "a]" =~ m[a\]] ? 1 : 0, "<>" =~ m<\<\>> ? 1 : 0;
say "a/b" =~ /a\/b/ ? 1 : 0;
my @w = ("hello  world" =~ m{
    (\w+)   # the first word
    \s+
    (\w+)   # the second
}x);
say "@w";
say "a b" =~ /a\ b/x ? 1 : 0, "a#b" =~ /a\#b/x ? 1 : 0, "aa" =~ /a +/x ? 1 : 0;
say "aaa" =~ /^(a+?)/ ? join("", "aaa" =~ /^(a+?)/) : "", "|", join("", "aaa" =~ /^(a{1,2})/), "|", join("", "aaa" =~ /^(a{1,2}?)/);
say join ",", "aab" =~ /(a|b)*/;
say join ",", "aab" =~ /(a)*b/;
say join ",", "ac" =~ /(a|b)*c/;
say "b" =~ /(a)?\1b/ ? 1 : 0, "aab" =~ /(a)\1b/ ? 1 : 0;
say "x" =~ /\bx\b/ ? 1 : 0, "_x" =~ /\bx/ ? 1 : 0, "éx" =~ /\Bx/ ? 1 : 0;
say "2+2" =~ /2\+2/ ? 1 : 0, "a.c" =~ /a\.c/ ? 1 : 0, "abc" =~ /a\.c/ ? 1 : 0;
say "\x{263A}" =~ /\x{263A}/ ? 1 : 0, "A" =~ /\x41/ ? 1 : 0, "A" =~ /\N{U+41}/ ? 1 : 0, "A" =~ /\o{101}/ ? 1 : 0;
say "a-" =~ /[a-]{2}/ ? 1 : 0, "-a" =~ /^[-a]+$/ ? 1 : 0, "é" =~ /[à-ê]/ ? 1 : 0, "a" =~ /[^\d\s]/ ? 1 : 0;
say 12345 =~ /^(\d)(\d+)$/ ? join("|", 12345 =~ /^(\d)(\d+)$/) : "no";
say 1.5 =~ /\./ ? 1 : 0, true =~ /^1$/ ? 1 : 0, false =~ /^$/ ? 1 : 0;
