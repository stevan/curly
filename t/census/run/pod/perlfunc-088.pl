use v5.42;
# Perl 5.36+
foreach my ($key, $value) (%{ +{ a => 1 } }) {
    print "$key=$value\n";
}
