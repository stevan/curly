use v5.42;
$_ = "ABC123";
if ( /^\D*(?!123)/ ) {                # Wrong!
    print "Yup, no 123 in $_\n";
}
