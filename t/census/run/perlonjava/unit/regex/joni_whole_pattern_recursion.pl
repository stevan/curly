use v5.42;

my $input = 'phoofoofoobarbarbarr';
my $match = $input =~ /foo(?R)?bar/ ? $& : undef;
say $match;

