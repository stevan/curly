use v5.42;
my ($x);
$x = "aaaa";
$x =~ /(a(?{print "Yow\n";}))*aa/;
