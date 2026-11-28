use v5.42;

###################
# Perl s///e vs s///ee Operator Tests

# Initial string with an arithmetic expression
my $string = "2+3";
my $pattern = qr/(\d+)\+(\d+)/;

# Using /e: Transform the expression into a string that represents another expression
my $result = $string =~ s/$pattern/"$1 * $2"/e; # This results in the string '2 * 3'
say(($result) ? "ok" : "not ok");
say((!($string ne '2 * 3')) ? "ok" : "not ok");

# Reset the string for /ee test
$string = "2+3";

# Using /ee: Evaluate the expression twice
# First evaluation: '2 + 3' -> '5'
# Second evaluation: '5' is treated as a string and evaluated again
$result = $string =~ s/$pattern/'$1 * $2'/ee;
say(($result) ? "ok" : "not ok");
say((!($string ne '6')) ? "ok" : "not ok");

###################
# End of Tests

