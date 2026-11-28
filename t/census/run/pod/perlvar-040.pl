use v5.42;
my ($str);
my @state;
sub matchit {
    push @state, $1;            # pushes "baz"
    my $str = shift;
    $str =~ /(zat)/;            # matches "zat"
    push @state, $1;            # pushes "zat"
}

{
    $str = "foo bar baz blorp zat";
    $str =~ /(foo)/;            # matches "foo"
    push @state, $1;            # pushes "foo"
    {
        $str =~ /(pizza)/;      # does NOT match
        push @state, $1;        # pushes "foo"
        $str =~ /(bar)/;        # matches "bar"
        push @state, $1;        # pushes "bar"
        $str =~ /(baz)/;        # matches "baz"
        matchit($str);          # see above
        push @state, $1;        # pushes "baz"
    }
    $str =~ s/noodles/rice/;    # does NOT match
    push @state, $1;            # pushes "foo"
    $str =~ s/(blorp)/zwoop/;   # matches "blorp"
    push @state, $1;            # pushes "blorp"
}
# the following prints "foo, foo, bar, baz, zat, baz, foo, blorp"
print join ",", @state;
