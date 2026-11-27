use v5.42;
my ($x, $y);
$x = "I like dogs.";
$y = $x =~ s/elephants/cougars/r;
print "$x $y\n"; # prints "I like dogs. I like dogs."
