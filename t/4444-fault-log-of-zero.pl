# kind: fault
# perl dies: Can't take log of 0 (T481).
use v5.42;
say log(1);
say log(0);
