use v5.42;
$_ = "123456789";
pos = 6;
s/.(?=.\G)/X/g;
print;      # prints 1234X6789, not XXXXX6789
