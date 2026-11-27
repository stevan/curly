# kind: fault
# perl takes a string with a point for a float, and prints 1e+15 (T487); the Num is D36's.
use v5.42;
say abs("-12.0");
say abs("-1000000000000000.0");
