use v5.42;

###################
# Perl @- and @+ Operator Tests

# Simple match - test @- and @+
my $string = "Hello World";
my $pattern = qr/(World)/;
my $match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test @- and @+ arrays for start and end positions
if ($match) {
    say(($-[0] == 6 && $+[0] == 11) ? "ok" : "not ok");
    say(($-[1] == 6 && $+[1] == 11) ? "ok" : "not ok");
}

# Match with multiple capture groups
$string = "Hello beautiful World";
$pattern = qr/(beautiful) (World)/;
$match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test @- and @+ for multiple capture groups
if ($match) {
    say(($-[0] == 6 && $+[0] == 21) ? "ok" : "not ok");
    say(($-[1] == 6 && $+[1] == 15) ? "ok" : "not ok");
    say(($-[2] == 16 && $+[2] == 21) ? "ok" : "not ok");
}

# Match with no captures
$string = "Just a simple string";
$pattern = qr/simple/;
$match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test @- and @+ with no capture groups
if ($match) {
    say(($-[0] == 7 && $+[0] == 13) ? "ok" : "not ok");
}

# Test with no match
$string = "No match here";
$pattern = qr/not_here/;
$match = $string =~ $pattern;
say((!($match)) ? "ok" : "not ok");

## # Ensure @- and @+ are not populated when there's no match
## if (!$match) {
##     print "not " if !(defined $-[0] || defined $+[0]);
##     say "ok # @- and @+ are not undef when no match occurs";
## }

