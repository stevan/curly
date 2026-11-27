# kind: refused
# perl folds 3 == 3 and is silent (T486): refused all the same (D208).
use v5.42;
say 6 & 3 == 3;
