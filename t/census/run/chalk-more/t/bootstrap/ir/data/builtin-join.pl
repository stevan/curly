use v5.42;
sub lit { return (10,20,30) }
my $j = join(",", lit());
print $j;
