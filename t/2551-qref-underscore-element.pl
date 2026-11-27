# kind: refused
# perl runs it, and warns: Use of uninitialized value $_[0] in string
use v5.42;
for (1) {
    say "$_[0]";
}
