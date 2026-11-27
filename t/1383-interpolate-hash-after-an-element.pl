# kind: fault
# perl dies: not a HASH reference (T203). A fault since step 13d, which takes the chain in.
use v5.42;
my @a = (1, 2, 3);
say "$a[0]{a}";
