# kind: refused
# perl prints A\.C, the run lost (T677).
use v5.42;
say "\Q\l\EA.C";
