use v5.42;
# DefinedOr
my $x;
my $y = $x // "fallback";
print "$y\n";
my $z = 0 // "unused";
print "$z\n";
