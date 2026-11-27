# t/models/io.py 4711
# env: CURLY_IO_A=one CURLY_IO_EMPTY= CURLY_IO_N=41 CURLY_IO_EQ=a=b
use v5.42;
say $ENV{CURLY_IO_A};
say "[$ENV{CURLY_IO_EMPTY}]";
say $ENV{CURLY_IO_N} + 1;
say $ENV{CURLY_IO_EQ};
say exists $ENV{CURLY_IO_EMPTY} ? "there" : "not";
say exists $ENV{CURLY_IO_NONE} ? "there" : "not";
say defined $ENV{CURLY_IO_NONE} ? "defined" : "undef";
say $ENV{CURLY_IO_NONE} // "default";
my @mine = sort grep { substr($_, 0, 8) eq "CURLY_IO" } keys %ENV;
say "@mine";
my $name = "CURLY_IO_A";
say "the value: $ENV{$name}";
my %copy = %ENV;
$copy{CURLY_IO_A} = "changed";
say $copy{CURLY_IO_A}, " ", $ENV{CURLY_IO_A};
my $r = \%ENV;
say $r->{CURLY_IO_N};
say defined $ENV{PATH} ? "path" : "none";
