use v5.42;
my $inner = '(.)\1';
"ABBA" =~ /^(.)(??{ $inner })\1/;
print $1; # prints "A";
