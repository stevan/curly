use v5.42;

my @cases = (
    [ qr/fooa++b/,     'fooaaaaab', 'possessive plus' ],
    [ qr/fooa*+b/,     'fooaaaaab', 'possessive star' ],
    [ qr/fooa{1,5}+b/, 'fooaaaaab', 'possessive bounded repeat' ],
    [ qr/fooa?+b/,     'fooab',     'possessive optional repeat' ],
);

for my $case (@cases) {
    my ($pattern, $input, $name) = @$case;
    my $match = $input =~ /$pattern/ ? $& : undef;
    say $match;
}

