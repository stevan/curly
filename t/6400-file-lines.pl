# t/models/file.py 6400
# file: full.txt=x y\nbc\nbc\nbc\n
# file: cut.txt=x y\n0.5\nx y
# file: empty.txt=
# file: one.txt=only\n
# file: blank.txt=\n\n
use v5.42;
sub show($s) {
    my @o;
    for my $i (0 .. length($s) - 1) {
        push @o, ord(substr($s, $i, 1));
    }
    return length($s) . ":" . join(",", @o);
}
open(my $fh, '<', "full.txt");
say eof($fh) ? "eof" : "more";
my $t1 = <$fh>; say defined $t1 ? show($t1) : "undef";
say eof($fh) ? "eof" : "more";
my $t2 = <$fh>; say defined $t2 ? show($t2) : "undef";
my $t3 = <$fh>; say defined $t3 ? show($t3) : "undef";
my $t4 = <$fh>; say defined $t4 ? show($t4) : "undef";
my $t5 = <$fh>; say defined $t5 ? show($t5) : "undef";
say eof($fh) ? "eof" : "more";
my $t6 = <$fh>; say defined $t6 ? show($t6) : "undef";
my $t7 = <$fh>; say defined $t7 ? show($t7) : "undef";
say eof($fh) ? "eof" : "more";
close($fh);
open($fh, '<', "cut.txt");
say eof($fh) ? "eof" : "more";
my $t8 = <$fh>; say defined $t8 ? show($t8) : "undef";
my $t9 = <$fh>; say defined $t9 ? show($t9) : "undef";
say eof($fh) ? "eof" : "more";
my $t10 = <$fh>; say defined $t10 ? show($t10) : "undef";
my $t11 = <$fh>; say defined $t11 ? show($t11) : "undef";
say eof($fh) ? "eof" : "more";
my $t12 = <$fh>; say defined $t12 ? show($t12) : "undef";
my $t13 = <$fh>; say defined $t13 ? show($t13) : "undef";
my $t14 = <$fh>; say defined $t14 ? show($t14) : "undef";
say eof($fh) ? "eof" : "more";
close($fh);
open($fh, '<', "empty.txt");
my $t15 = <$fh>; say defined $t15 ? show($t15) : "undef";
say eof($fh) ? "eof" : "more";
my $t16 = <$fh>; say defined $t16 ? show($t16) : "undef";
my $t17 = <$fh>; say defined $t17 ? show($t17) : "undef";
my $t18 = <$fh>; say defined $t18 ? show($t18) : "undef";
my $t19 = <$fh>; say defined $t19 ? show($t19) : "undef";
my $t20 = <$fh>; say defined $t20 ? show($t20) : "undef";
say eof($fh) ? "eof" : "more";
my $t21 = <$fh>; say defined $t21 ? show($t21) : "undef";
say eof($fh) ? "eof" : "more";
close($fh);
open($fh, '<', "one.txt");
say eof($fh) ? "eof" : "more";
my $t22 = <$fh>; say defined $t22 ? show($t22) : "undef";
my $t23 = <$fh>; say defined $t23 ? show($t23) : "undef";
say eof($fh) ? "eof" : "more";
my $t24 = <$fh>; say defined $t24 ? show($t24) : "undef";
my $t25 = <$fh>; say defined $t25 ? show($t25) : "undef";
my $t26 = <$fh>; say defined $t26 ? show($t26) : "undef";
my $t27 = <$fh>; say defined $t27 ? show($t27) : "undef";
say eof($fh) ? "eof" : "more";
my $t28 = <$fh>; say defined $t28 ? show($t28) : "undef";
say eof($fh) ? "eof" : "more";
close($fh);
open($fh, '<', "blank.txt");
my $t29 = <$fh>; say defined $t29 ? show($t29) : "undef";
my $t30 = <$fh>; say defined $t30 ? show($t30) : "undef";
say eof($fh) ? "eof" : "more";
my $t31 = <$fh>; say defined $t31 ? show($t31) : "undef";
say eof($fh) ? "eof" : "more";
my $t32 = <$fh>; say defined $t32 ? show($t32) : "undef";
my $t33 = <$fh>; say defined $t33 ? show($t33) : "undef";
my $t34 = <$fh>; say defined $t34 ? show($t34) : "undef";
my $t35 = <$fh>; say defined $t35 ? show($t35) : "undef";
say eof($fh) ? "eof" : "more";
close($fh);
