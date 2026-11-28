use v5.42;

my $scalar = 'value';
my $object = bless {}, 'Local::Downgrade::Object';
my @references = (
    [ CODE   => sub { 42 } ],
    [ ARRAY  => [] ],
    [ HASH   => {} ],
    [ SCALAR => \$scalar ],
    [ 'Local::Downgrade::Object' => $object ],
);

for my $case (@references) {
    my ($expected_type, $value) = @$case;
    say utf8::downgrade($value, 1);
    say ref($value);
}

say $references[0][1]->();

