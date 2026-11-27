# kind: fault
# perl gives -0 or 0.
use v5.42;
say sqrt(" -0.0");
