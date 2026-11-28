# t/models/file.py 6407
# file: u.txt=caf\0303\0251\n\0342\0230\0272 and \0360\0237\0230\0200\n\0357\0273\0277bom
use v5.42;
use utf8;
use open ':std', ':encoding(UTF-8)';
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
open(my $fh, '<', "u.txt") or die "cannot open u.txt: $!\n";
my @a1 = <$fh>; say scalar(@a1), " lines"; for my $x (@a1) { say show($x) }
close($fh);
open(my $out, '>', "w.txt") or die "cannot open w.txt: $!\n";
print $out "é", chr(9786), "\n";
say $out chr(0x10FFFD), "ñ";
printf $out "%s|%3s|\n", "ü", "é";
close($out);
open($fh, '<', "w.txt");
my @a2 = <$fh>; say scalar(@a2), " lines"; for my $x (@a2) { say show($x) }
close($fh);
open($fh, '<', "w.txt");
my $first = <$fh>; print $first;
close($fh);
