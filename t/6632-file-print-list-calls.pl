# By hand, with perl's answers (the independent review of step 21b; T697, D287): what a print's list may do while
# the handle is in perl's hand: change other variables, read the handle's variable, and take the handle from a
# call, whose value holds it.
# file: in.txt=a\n
use v5.42;
open(my $w, '>', 'made.txt') or die "no\n";
my $n = 0;
sub count() {
    $n++;
    return $n;
}
sub is_open() {
    return defined($w) ? 'open' : 'not';
}
print $w count(), ' ', is_open(), "\n";
say $w count(), ' ', ref($w);
printf $w "%d %s\n", count(), is_open();
my @held = ($w);
print { $held[0] } count(), ' ', scalar(@held), "\n";
my %held = (out => $w);
say { $held{out} } count(), ' ', join(',', sort keys %held);
sub out() {
    return $w;
}
print { out() } count(), "\n";
sub maker() {
    open(my $t, '>>', 'other.txt') or die "no\n";
    return $t;
}
print { maker() } count(), "\n";
close($w);
for my $name ('made.txt', 'other.txt') {
    open(my $r, '<', $name) or die "no $name\n";
    print "$name: ", <$r>;
    close($r);
}
