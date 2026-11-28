use v5.42;
printf "%vd", "AB\x{100}";           # prints "65.66.256"
printf "version is v%vd\n", $^V;     # Perl's version
