use v5.42;

BEGIN {
    *CORE::GLOBAL::sqrt = sub { CORE::sqrt(shift) };
}

my $original = *CORE::GLOBAL::sqrt{CODE};
no warnings 'redefine';
*CORE::GLOBAL::sqrt = sub {
    $_[0]++;
    goto &$original;
};

my $value = 99;
say sqrt($value);

