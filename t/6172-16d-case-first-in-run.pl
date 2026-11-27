# kind: refused
# perl gives 'hELLO' (\l of the rest, inside the \U).
use v5.42;
say "\Uh\lello";
