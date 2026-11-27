use v5.42;
for ( 1..3 ){
    $\ = "\r\n";
    nasty_break();
    print "$_";
}

sub nasty_break {
    $\ = "\f";
    # do something with $_
}
