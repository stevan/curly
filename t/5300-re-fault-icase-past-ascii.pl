# kind: fault
# perl folds by Unicode's tables: "Ka" =~ /k/i is 1, and "\x{212A}" (the
# Kelvin sign) =~ /k/i is 1 too (T546).
use v5.42;
say "Ka" =~ /k/i ? 1 : 0;
say "\x{212A}" =~ /k/i ? 1 : 0;
