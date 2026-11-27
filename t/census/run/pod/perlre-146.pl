use v5.42;
my ($count);
'aaabaaab' =~ /a+b?(*SKIP)(?{print "$&\n"; $count++})(*FAIL)/;
print "Count=$count\n";
