# kind: fault
# perl dies: Can't take log of -1.
use v5.42;
say log(-1);
