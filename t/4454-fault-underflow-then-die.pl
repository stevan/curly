# kind: fault
# perl exits 34, the ERANGE exp set (T472, D151).
use v5.42;
my $v = -745.2;
my $x = exp($v);
say "after";
die "x\n";
