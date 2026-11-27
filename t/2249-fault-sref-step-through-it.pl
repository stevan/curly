# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my @m = (undef);
${ $_ }++ for @m;
say(2);
