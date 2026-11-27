use v5.42;
my %count;
"supercalifragilisticexpialidocious" =~
    /([aeiou])(?{ $count{lc($1)}++; })(*FAIL)/i;
printf "%3d '%s'\n", $count{$_}, $_ for (sort keys %count);
