# perl prints ABC: the case escapes come with interpolation (D43), and
# are in since step 16d (D256).
use v5.42;
say "\Uabc\E";
