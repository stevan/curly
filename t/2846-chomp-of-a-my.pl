# perl declares $t, assigns it and chomps it; refused until step 21a (D219).
use v5.42;
my $s = "ab\n";
chomp(my $t = $s);
say "[$t]";
