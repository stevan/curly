# kind: same
# What the breakages of the step showed no test reached
# (briefs/step19-mutations.py): $ and \A under /m, \n in a pattern, and
# which alternative is taken first, a backreference under /i, and how
# many characters a capture past ASCII holds; and m, s, y and tr as words
# before =>, and in braces (son-audit/f/c60.pl, from the census).
use v5.42;
say "a\nb" =~ /a$/ ? 1 : 0, "a\nb" =~ /a$/m ? 1 : 0, "a\nb\n" =~ /b$/m ? 1 : 0;
my @lines = ("one\ntwo\nthree" =~ /(\w+)$/mg);
say "@lines";
say "x\na" =~ /\Aa/m ? 1 : 0, "x\na" =~ /^a/m ? 1 : 0, "a\nx" =~ /\Aa/m ? 1 : 0;
say "a\nb" =~ /a\nb/ ? 1 : 0, "a\rb" =~ /a\nb/ ? 1 : 0, "a\rb" =~ /a\rb/ ? 1 : 0, "a\tb" =~ /a\tb/ ? 1 : 0;
say join ",", "ab" =~ /(a|ab)/, "ab" =~ /(ab|a)/, "abc" =~ /(a|ab)(c|bc)/;
say "aA" =~ /^(a)\1$/i ? 1 : 0, "Ab" =~ /^(a)\1$/i ? 1 : 0;
my @c = ("x\x{e9}\x{263A}y" =~ /x(..)y/);
say length($c[0]), " ", ord(substr($c[0], 1));
my %h = (m => 1, s => 2, y => 3, tr => 4);
say $h{m} + $h{s} + $h{y} + $h{tr};
my $o = {m => {a => 1}};
say $o->{m}{a};
