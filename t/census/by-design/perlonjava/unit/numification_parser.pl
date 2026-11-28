use v5.42;

# Test basic integer parsing
my $int = 42;
say $int;

# Test negative integer parsing
my $neg_int = -42;
say $neg_int;

# Test floating point parsing
my $float = 3.14;
say $float;

# Test negative floating point parsing
my $neg_float = -3.14;
say $neg_float;

# Test hexadecimal parsing
my $hex = 0xFF;
say $hex;

# Test hexadecimal parsing with uppercase letters
my $hex_upper = 0x1A;
say $hex_upper;

# Test octal parsing
my $octal = 0755;
say $octal;

# Test binary parsing
my $binary = 0b1010;
say $binary;

# Test scientific notation
my $sci = 1.5e3;
say $sci;

# Test hexadecimal floating point parsing
my $hex_float = 0x1.999ap-4;
say sprintf("%.6f", $hex_float);

# Test hexadecimal floating point parsing with uppercase P
my $hex_float_upper = 0x1.999AP-4;
say sprintf("%.6f", $hex_float_upper);

# Test zero
my $zero = 0;
say $zero;

# Test very large number
my $large_num = 1e308;
say $large_num;

# Test very small number
my $small_num = 1e-308;
say $small_num;


