# What the matcher does to answer sooner must change no answer (D240 to
# D242): each line here is one that a mistake in it gets wrong.
use v5.42;
use utf8;
use open ':std', ':encoding(UTF-8)';
# A backreference reads a capture, so the same place of the pattern at the
# same place of the string may fail once and match the next time: nothing
# is remembered then.
say "abcab" =~ /^(a|ab)(?:b|x)?c\1$/ ? 1 : 0;
say "abcab" =~ /^(a|ab)b*c\1$/ ? 1 : 0;
say "aabaab" =~ /^(a+)(?:a|b)+\1b$/ ? 1 : 0;
say "xyxyzxy" =~ /^(x|xy)(?:y|xy)*z\1$/ ? 1 : 0;
say join("|", ("abcab" =~ /^(a|ab)b*c\1$/)), ".";
# Two places of a pattern at one place of the string are two.
say "ax" =~ /(?:(?:a|b)|c)x/ ? 1 : 0;
say "ab" =~ /(?:a|b)?(?:a|b)?b/ ? 1 : 0;
say "aa" =~ /^(?:a*|b)(?:a*|c)$/ ? 1 : 0;
say "abab" =~ /^(?:(?:ab)*|x)(?:(?:ab)*|y)$/ ? 1 : 0;
say "aaa" =~ /^a*?a*?a$/ ? 1 : 0;
# What a group holds is what it held on the way that matched.
say join("|", ("aaab" =~ /^(a*)(a*)b/)), ".";
say join("|", ("aaab" =~ /^(a*?)(a*)b/)), ".";
say join("|", ("aaab" =~ /^(a+)(a+)b/)), ".";
say join("|", ("aaab" =~ /(a|aa)(a|aa)b/)), ".";
say join("|", map { $_ // "u" } ("ab" =~ /(?:(a)|(b))$/)), ".";
say join("|", map { $_ // "u" } ("aab" =~ /^(a)*?(a*)(c)?b/)), ".";
say join("|", ("abcd" =~ /(.*)(c|bc)(d?)$/)), ".";
say join("|", ("abcd" =~ /(.*?)(c|bc)(d?)$/)), ".";
# A run gives back a character at a time, whole characters, and no more
# than it took.
say join("|", ("ééx" =~ /^(.*)é/)), ".";
say join("|", ("é٣éx" =~ /^(\w*)\wx/)), ".";
say join("|", ("ééé" =~ /^(é*)éé$/)), ".";
say join("|", ("日本語語" =~ /^(.*)語/)), ".";
say join("|", map { length($_) } ("éé" =~ /^(.*)(.)/)), ".";
say join("|", map { length($_) } ("日本語" =~ /^([^x]+)([^x])/)), ".";
say join("|", map { length($_) } ("ééé" =~ /(\w*)(\w)(.)/)), ".";
# A run that comes to where a run has been gives back what it took before
# that, a character at a time.
say "abbbc" =~ /^(?:ab|a)b*bbbc$/ ? 1 : 0;
say join("|", ("abbbc" =~ /^(ab|a)(b*)bbbc$/)), ".";
say "xyyyz" =~ /(?:xy|x)y*yyz/ ? 1 : 0;
say "xaab" =~ /xa(a*)aab/ ? 1 : 0;
say "xab" =~ /x(a*)ab/ ? 1 : 0;
say "xb" =~ /x(a*)ab/ ? 1 : 0;
say "ab" =~ /^a(b*)bb/ ? 1 : 0;
say join("|", ("xaaab" =~ /x(a*)ab/)), ".";
say join("|", ("xaaab" =~ /x(a*)(a*)(a*)b/)), ".";
say join("|", ("aaa" =~ /^(a*)(a*)$/)), ".";
say join("|", ("a\nb" =~ /(.*)(.*)/s)), ".";
say join("|", ("a\nb" =~ /(.*)\n(.*)/)), ".";
# Where a match may start: anywhere, unless the pattern begins with ^.
say "ab" =~ /b/ ? 1 : 0;
say "ab" =~ /^b/ ? 1 : 0;
say "a\nb" =~ /^b/ ? 1 : 0;
say "a\nb" =~ /^b/m ? 1 : 0;
say "a\nb" =~ /\Ab/m ? 1 : 0;
say "ab" =~ /^a|b/ ? 1 : 0;
say "ab" =~ /(?:^a)?b$/ ? 1 : 0;
say join("|", ("ab" =~ /(^a|b)/g)), ".";
say join("|", ("aaa" =~ /^a/g)), ".";
say join("|", ("a\na\na" =~ /^a/mg)), ".";
say join("|", ("aaa" =~ /a/g)), ".";
say join("|", ("banana" =~ /ana/g)), ".";
say join("|", ("banana" =~ /a(n?)/g)), ".";
say "éa" =~ /a/ ? 1 : 0;
say "èéa" =~ /éa/ ? 1 : 0;
say "èé" =~ /éa/ ? 1 : 0;
say "日本語" =~ /語/ ? 1 : 0;
say "日本語" =~ /本語$/ ? 1 : 0;
say "日本" =~ /語/ ? 1 : 0;
say "aB" =~ /b/ ? 1 : 0;
say "aB" =~ /b/i ? 1 : 0;
say "aB" =~ /A/i ? 1 : 0;
say "" =~ /a/ ? 1 : 0;
say "" =~ /^/ ? 1 : 0;
say "b" =~ /a{0}b/ ? 1 : 0;
say "xb" =~ /a?b/ ? 1 : 0;
