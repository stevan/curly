use v5.42;
print sort { $::a cmp $::b }           qw(A C E G B D F H);
                                       # OK
print sort { our $a cmp our $b }       qw(A C E G B D F H);
                                       # also OK
print sort { our ($a, $b); $a cmp $b } qw(A C E G B D F H);
                                       # also OK
sub lexi { our $a cmp our $b }
print sort lexi                        qw(A C E G B D F H);
                                       # also OK
# the above print ABCDEFGH
