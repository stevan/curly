use v5.42;
my $buf = pack( 'iii', 100, 20, 3 );
print unpack( '%32i3', $buf ), "\n";  # prints 123
