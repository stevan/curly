# /g over long strings (T568, D240, D244): the limit and what the matcher
# remembers are one match operation's, every match of the /g. And small
# ones where a match must begin where the last ended, and go again through
# what the last one went through there.
use v5.42;
my $words = (("w" x 999) . " ") x 3000;
my @l = ($words =~ /(\w+)/g);
say scalar(@l), " ", length($l[0]), " ", length($l[2999]);
@l = ($words =~ /\w+/g);
say scalar(@l);
@l = ($words =~ /(\w+) (\w)/g);
say scalar(@l), " ", length($l[0]), " ", length($l[1]);
@l = ($words =~ /\s+/g);
say scalar(@l);
@l = ($words =~ /w{999}/g);
say scalar(@l);
@l = ($words =~ /x*y/g);
say scalar(@l);
@l = ($words =~ /(?:w+ ){1000}/g);
say scalar(@l), " ", length($l[0]);
my $pairs = "k=v;" x 2000;
@l = ($pairs =~ /(\w+)=(\w*);/g);
say scalar(@l);
@l = ($pairs =~ /;/g);
say scalar(@l);
@l = ($pairs =~ /[^;]*;/g);
say scalar(@l);
@l = ($pairs =~ /[^;]*/g);
say scalar(@l);
# After a match, the next begins where it ended.
say join("|", ("baa" =~ /a*/g)), ".";
say join("|", ("aab" =~ /a*/g)), ".";
say join("|", ("aab" =~ /a*?/g)), ".";
say join("|", ("abab" =~ /(?:ab)*/g)), ".";
say join("|", ("abab" =~ /(?:a|b)*?/g)), ".";
say join("|", ("aaa" =~ /a|/g)), ".";
say join("|", ("aaa" =~ /|a/g)), ".";
say join("|", ("abcabc" =~ /(?:a|ab)(?:c|bc)?/g)), ".";
say join("|", ("xaxbx" =~ /x?[ab]?/g)), ".";
say join("|", ("aaab" =~ /a{0,2}/g)), ".";
say join("|", ("aaab" =~ /a{0,2}?/g)), ".";
say join("|", ("a,b,,c" =~ /[^,]*/g)), ".";
say join("|", ("one two" =~ /\w*\b/g)), ".";
say join("|", ("a\nb\n" =~ /^.*$/mg)), ".";
say join("|", ("a\nb\n" =~ /^/mg)), ".";
say join("|", ("a\nb\n" =~ /$/mg)), ".";
say join("|", ("aXbXc" =~ /(.*?)X/g)), ".";
say join("|", ("aXbXc" =~ /(.*)X/g)), ".";
say join("|", ("ab" =~ /(a?)(b?)/g)), ".";
