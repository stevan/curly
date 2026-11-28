use v5.42;
print sort { $a cmp $b }               qw(A C E G B D F H);
                                       # WRONG
sub badlexi { $a cmp $b }
print sort badlexi                     qw(A C E G B D F H);
                                       # WRONG
# the above prints BACFEDGH or some other incorrect ordering
