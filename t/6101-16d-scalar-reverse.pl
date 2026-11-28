# scalar reverse: the list joined, its characters reversed (D258).
use v5.42;
my $s = "abc";
say scalar reverse $s;
say scalar reverse("ab", "cd");
say scalar(reverse("x", "y"));
say scalar reverse "dlrow ,", "olleH";
my @a = ("x", "yz");
say scalar reverse @a;
say lc scalar reverse "AB";
say scalar reverse 12, 3.5;
my @e = ("");
say "[", scalar reverse(@e), "]";
sub rev($w) {
    return scalar reverse $w;
}
say rev("stressed");
