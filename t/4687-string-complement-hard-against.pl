# kind: refused
# perl takes ~. for the string operator: ~."5".
use v5.42;
say ~.5;
