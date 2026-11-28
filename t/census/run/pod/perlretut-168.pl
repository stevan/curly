use v5.42;
my ($s);
my $pp = qr/^(\W* (?: (\w) (?1) \g{-1} | \w? ) \W*)$/ix;
for $s ( "saippuakauppias", "A man, a plan, a canal: Panama!" ){
    print "'$s' is a palindrome\n" if $s =~ /$pp/;
}
