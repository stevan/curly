# kind: fault
# perl gives the unsigned integer 9300000000000000000 (T470).
use v5.42;
say int(9.2e18);
say int(9.3e18);
