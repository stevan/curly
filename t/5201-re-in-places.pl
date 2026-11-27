# kind: same
# A match where one value is wanted and where a list is, in each place
# the language has (step 19; D235).
use v5.42;
sub first_digits($s) {
    return $s =~ /(\d+)/;
}
sub pairs($s) {
    return $s =~ /(\w)(\w)/g;
}
sub is_word($s) {
    $s =~ /^\w+$/;
}
my $n = first_digits("ab12cd");
say $n;
my @d = first_digits("ab12cd");
say "@d";
my @none = first_digits("abc");
say scalar(@none);
my @p = pairs("abcd");
say "@p";
say is_word("abc") ? "word" : "not", is_word("a b") ? "word" : "not";
my @words = grep { $_ =~ /^b/ } ("apple", "banana", "blue");
say "@words";
my @nums = map { $_ =~ /(\d+)/ } ("a1", "b", "c22");
say "@nums";
my @sorted = sort { ($a =~ /(\d+)/)[0] <=> ($b =~ /(\d+)/)[0] } ("x10", "y9", "z100");
say "@sorted";
for my $w ("one two" =~ /(\w+)/g) {
    say "[$w]";
}
my %h = ("k=v" =~ /(\w)=(\w)/);
say join ",", map { "$_$h{$_}" } sort keys %h;
my @all = ("a,b,,c" =~ /([^,]*)/g);
say scalar(@all), ":", join("|", @all);
say(("abc" =~ /b/) + 1);
my $t = "abc" =~ /c$/;
say $t ? "true" : "false";
my $r = ["xyz"];
say $r->[0] =~ /y/ ? 1 : 0;
my %g = (s => "q9");
say $g{s} =~ /\d/ ? 1 : 0;
my $u = "hay";
if ($u =~ /a/ && $u !~ /z/) {
    say "both";
}
say "t" =~ /t/ && "u" =~ /u/ ? "and" : "no";
my @x = ("ab" =~ /(a)/, "cd" =~ /(d)/);
say "@x";
