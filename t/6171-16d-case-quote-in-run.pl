# kind: refused
# perl quotes inside the \U: 'AB\.CD.E'.
use v5.42;
say "\Ua\Qb.c\Ed.e";
