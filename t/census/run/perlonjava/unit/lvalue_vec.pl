use v5.42;

# Basic lvalue vec() usage
my $str18 = "abcd";
vec($str18, 0, 8) = 65;  # ASCII value of 'A'
say $str18;

# lvalue vec() with different bit width
my $str19 = "abcd";
vec($str19, 0, 16) = 16706;  # 'AB' as 16-bit integer
say substr($str19, 0, 2);

# lvalue vec() with non-zero offset
my $str20 = "abcd";
vec($str20, 1, 8) = 66;  # ASCII value of 'B'
say $str20;

# lvalue vec() with larger bit width
my $str21 = "abcdefgh";
vec($str21, 0, 32) = 0x41424344;  # 'ABCD' as 32-bit integer
say substr($str21, 0, 4);

# lvalue vec() beyond string length
my $str22 = "ab";
vec($str22, 2, 8) = 67;  # ASCII value of 'C'
say $str22;

# lvalue vec() with bit width of 1
my $str23 = "\x55";  # Binary: 01010101
vec($str23, 3, 1) = 1;
say ord($str23);

# Combining multiple lvalue vec() calls
my $str24 = "\0\0";
vec($str24, 0, 8) = 65;  # ASCII value of 'A'
vec($str24, 1, 8) = 66;  # ASCII value of 'B'
say $str24;

