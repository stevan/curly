use v5.42;
my $buf = pack( 'p', "abc\x00efhijklmn" );
print unpack( 'p', $buf );    # prints "abc"
