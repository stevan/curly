# t/models/file.py 6403
use v5.42;
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
open(my $out, '>', "made.txt") or die "cannot open made.txt: $!\n";
print $out "first ", 1, "\n";
say $out "second", 2;
printf $out "%s-%03d-%.2f\n", "x", 7, 1.5;
print {$out} "block\n";
say { $out } "spaced";
printf {$out} "%d%%\n", 5;
print $out 0.5, " ", -3, " ", 1e+21, "\n";
close($out) or die "cannot close: $!\n";
open(my $in, '<', "made.txt") or die "cannot open made.txt: $!\n";
my @a1 = <$in>; say scalar(@a1), " lines"; for my $x (@a1) { say show($x) }
close($in);
open($out, '>>', "made.txt");
print $out "added\n";
close($out);
open($out, '>>', "new.txt");
print $out "no newline";
close($out);
open($out, '>', "none.txt");
close($out);
open($in, '<', "made.txt");
my @a2 = <$in>; say scalar(@a2), " lines"; for my $x (@a2) { say show($x) }
close($in);
open($in, '<', "new.txt");
my @a3 = <$in>; say scalar(@a3), " lines"; for my $x (@a3) { say show($x) }
close($in);
open($in, '<', "none.txt");
my @a4 = <$in>; say scalar(@a4), " lines"; for my $x (@a4) { say show($x) }
close($in);
open($out, '>', "made.txt");
say $out "again";
say close($out);
open($in, '<', "made.txt");
my @a5 = <$in>; say scalar(@a5), " lines"; for my $x (@a5) { say show($x) }
close($in);
open($out, '>', "here.txt");
print $out <<"END";
from a heredoc here
END
my @items = (1, 2, 3);
print $out "@items", "\n", scalar(@items), "\n";
say $out join("-", map { $_ * 2 } @items);
print $out !1, "|", !0, "\n";
close($out);
open($in, '<', "here.txt");
my @a6 = <$in>; say scalar(@a6), " lines"; for my $x (@a6) { say show($x) }
close($in);
