use v5.42;
my ($foo);
print ++($foo = "99");      # prints "100"
print ++($foo = "a0");      # prints "a1"
print ++($foo = "Az");      # prints "Ba"
print ++($foo = "zz");      # prints "aaa"
