# perl prints a to stdout; refused until step 21a took STDOUT (D218).
use v5.42;
printf STDOUT "%s\n", "a";
