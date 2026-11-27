# kind: refused
# perl takes &. for the string operator: 6 &.5 is "6" &. "5", 4 (the review's finding 6).
use v5.42;
say 6 &.5;
