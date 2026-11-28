use v5.42;
my $string = "supercalifragilisticexpialidocious";
my %count;
$count{lc($1)}++ while $string =~ /([aeiou])/ig;
printf "%3d '%s'\n", $count{$_}, $_ for (sort keys %count);
