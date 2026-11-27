# check: fails: differs from perl
# A variable the test did not set is not there for perl (D220): HOME is
# the machine's, and neither perl nor the program is given it.
use v5.42;
say defined $ENV{HOME} ? "home" : "none";
