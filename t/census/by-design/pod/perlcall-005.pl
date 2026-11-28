use v5.42;
sub fred
  { print "@_\n"  }

sub joe
  { &fred }

&joe(1,2,3);
