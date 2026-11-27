use v5.42;
use experimental 'class';
class Range { field $lo :param :reader; field $hi :param :reader; method floor { $lo } method ceil { $hi } } my $r = Range->new(lo => 1, hi => 5); say $r->floor, "..", $r->ceil;
