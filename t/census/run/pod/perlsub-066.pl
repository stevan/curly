use v5.42;
my $secret_version = '1.001-beta';
my $secret_sub = sub { print $secret_version };
$secret_sub->();
