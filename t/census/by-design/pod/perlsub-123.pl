use v5.42;
my ($wref, $xref, @y, @z);
($wref, $xref) = func(\@y, \@z);
print "@$wref has more than @$xref\n";
sub func {
    my ($yref, $zref) = @_;
    if (@$yref > @$zref) {
        return ($yref, $zref);
    } else {
        return ($zref, $yref);
    }
}
