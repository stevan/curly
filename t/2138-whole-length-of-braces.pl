# kind: refused
# perl runs it: '1\n', and warns: length() used on @array.
use v5.42;
my $r = [1, 2];
say length(@{$r});
