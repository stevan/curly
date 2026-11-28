use v5.42;
use warnings;
my (@xyz, $x, $y, $z);

@xyz = (1, 2, 3);
print "@xyz\n";                             # 1 2 3

@xyz = ('al', 'be', 'ga', 'de');
print "@xyz\n";                             # al be ga de

@xyz = (101, 102);
print "@xyz\n";                             # 101 102
