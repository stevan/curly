# t/models/file.py 6401
# file: five.txt=0\nx y\n\n-1\n42\n
# file: cut.txt=0\n-1\nq\0011z\n
# file: empty.txt=
use v5.42;
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
sub count(@lines) { return scalar(@lines) }
open(my $fh, '<', "five.txt");
my $t1 = <$fh>; say defined $t1 ? show($t1) : "undef";
my @a2 = <$fh>; say scalar(@a2), " lines"; for my $x (@a2) { say show($x) }
my @a3 = <$fh>; say scalar(@a3), " lines"; for my $x (@a3) { say show($x) }
my $t4 = <$fh>; say defined $t4 ? show($t4) : "undef";
close($fh);
open($fh, '<', "cut.txt");
my @a5 = <$fh>; say scalar(@a5), " lines"; for my $x (@a5) { say show($x) }
my @a6 = <$fh>; say scalar(@a6), " lines"; for my $x (@a6) { say show($x) }
my $t7 = <$fh>; say defined $t7 ? show($t7) : "undef";
close($fh);
open($fh, '<', "empty.txt");
my @a8 = <$fh>; say scalar(@a8), " lines"; for my $x (@a8) { say show($x) }
my @a9 = <$fh>; say scalar(@a9), " lines"; for my $x (@a9) { say show($x) }
my $t10 = <$fh>; say defined $t10 ? show($t10) : "undef";
close($fh);
open($fh, '<', "five.txt");
my $t11 = <$fh>; say defined $t11 ? show($t11) : "undef";
my ($a12, @a12) = <$fh>; say defined $a12 ? show($a12) : "undef", " then ", scalar(@a12);
my ($a13, @a13) = <$fh>; say defined $a13 ? show($a13) : "undef", " then ", scalar(@a13);
my $t14 = <$fh>; say defined $t14 ? show($t14) : "undef";
close($fh);
open($fh, '<', "cut.txt");
my $t15 = <$fh>; say defined $t15 ? show($t15) : "undef";
my ($a16, @a16) = <$fh>; say defined $a16 ? show($a16) : "undef", " then ", scalar(@a16);
my ($a17, @a17) = <$fh>; say defined $a17 ? show($a17) : "undef", " then ", scalar(@a17);
my $t18 = <$fh>; say defined $t18 ? show($t18) : "undef";
close($fh);
open($fh, '<', "empty.txt");
my ($a19, @a19) = <$fh>; say defined $a19 ? show($a19) : "undef", " then ", scalar(@a19);
my ($a20, @a20) = <$fh>; say defined $a20 ? show($a20) : "undef", " then ", scalar(@a20);
my $t21 = <$fh>; say defined $t21 ? show($t21) : "undef";
close($fh);
open($fh, '<', "five.txt");
for my $x (<$fh>) { say "for ", show($x) }
for my $x (<$fh>) { say "for ", show($x) }
my $t24 = <$fh>; say defined $t24 ? show($t24) : "undef";
close($fh);
open($fh, '<', "cut.txt");
my $t25 = <$fh>; say defined $t25 ? show($t25) : "undef";
for my $x (<$fh>) { say "for ", show($x) }
for my $x (<$fh>) { say "for ", show($x) }
my $t28 = <$fh>; say defined $t28 ? show($t28) : "undef";
close($fh);
open($fh, '<', "empty.txt");
my $t29 = <$fh>; say defined $t29 ? show($t29) : "undef";
for my $x (<$fh>) { say "for ", show($x) }
for my $x (<$fh>) { say "for ", show($x) }
my $t32 = <$fh>; say defined $t32 ? show($t32) : "undef";
close($fh);
open($fh, '<', "five.txt");
my $t33 = <$fh>; say defined $t33 ? show($t33) : "undef";
say count(<$fh>);
say count(<$fh>);
my $t36 = <$fh>; say defined $t36 ? show($t36) : "undef";
close($fh);
open($fh, '<', "cut.txt");
my $t37 = <$fh>; say defined $t37 ? show($t37) : "undef";
say count(<$fh>);
say count(<$fh>);
my $t40 = <$fh>; say defined $t40 ? show($t40) : "undef";
close($fh);
open($fh, '<', "empty.txt");
say count(<$fh>);
say count(<$fh>);
my $t43 = <$fh>; say defined $t43 ? show($t43) : "undef";
close($fh);
open($fh, '<', "five.txt");
my $t44 = <$fh>; say defined $t44 ? show($t44) : "undef";
while (my $l = <$fh>) { say "while ", show($l) }
while (my $l = <$fh>) { say "while ", show($l) }
my $t47 = <$fh>; say defined $t47 ? show($t47) : "undef";
close($fh);
open($fh, '<', "cut.txt");
my $t48 = <$fh>; say defined $t48 ? show($t48) : "undef";
while (my $l = <$fh>) { say "while ", show($l) }
while (my $l = <$fh>) { say "while ", show($l) }
my $t51 = <$fh>; say defined $t51 ? show($t51) : "undef";
close($fh);
open($fh, '<', "empty.txt");
while (my $l = <$fh>) { say "while ", show($l) }
while (my $l = <$fh>) { say "while ", show($l) }
my $t54 = <$fh>; say defined $t54 ? show($t54) : "undef";
close($fh);
