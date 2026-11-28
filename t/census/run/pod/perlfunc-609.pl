use v5.42;
my $foo = '';
vec($foo,  0, 32) = 0x5065726C; # 'Perl'

# $foo eq "Perl" eq "\x50\x65\x72\x6C", 32 bits
print vec($foo, 0, 8);  # prints 80 == 0x50 == ord('P')

vec($foo,  2, 16) = 0x5065; # 'PerlPe'
vec($foo,  3, 16) = 0x726C; # 'PerlPerl'
vec($foo,  8,  8) = 0x50;   # 'PerlPerlP'
vec($foo,  9,  8) = 0x65;   # 'PerlPerlPe'
vec($foo, 20,  4) = 2;      # 'PerlPerlPe'   . "\x02"
vec($foo, 21,  4) = 7;      # 'PerlPerlPer'
                               # 'r' is "\x72"
vec($foo, 45,  2) = 3;      # 'PerlPerlPer'  . "\x0c"
vec($foo, 93,  1) = 1;      # 'PerlPerlPer'  . "\x2c"
vec($foo, 94,  1) = 1;      # 'PerlPerlPerl'
                               # 'l' is "\x6c"
