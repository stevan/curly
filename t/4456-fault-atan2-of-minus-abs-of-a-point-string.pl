# kind: fault
# perl's abs("0.0") is a float, so its negation is -0, and atan2 prints pi (the review's finding 2).
use v5.42;
say atan2(0, -abs("0"));
say atan2(0, -abs("0.0"));
