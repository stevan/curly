# t/models/file.py 6412
# file: in.txt=a\n
use v5.42;
open(my $h1, '<', "in.txt") or die "cannot open in.txt: $!\n";
open(my $h2, '<', "in.txt") || die "cannot open in.txt: $!\n";
my $h3;
die "cannot open in.txt: $!\n" unless open($h3, '<', "in.txt");
open(my $h4, '<', "in.txt") or die "cannot open in.txt: $!";
close($h1) or die "cannot close: $!\n";
close $h2;
close $h3 or die "cannot close: $!\n";
close($h4) || die "cannot close: $!\n";
my $ok = 1;
open($h1, '<', 'in.txt') or die "no\n" if $ok;
close $h1 if $ok;
say "all opened and closed";
