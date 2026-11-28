use v5.42;
my ($greeting);
$greeting = "World";
print "It matches\n" if "Hello World" =~ /$greeting/;
