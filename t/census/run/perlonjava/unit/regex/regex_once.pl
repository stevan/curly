use v5.42;

###################
# Perl m?PAT? Operator Tests

# Simple match that should only match once without reset
my $string  = "apple orange apple";
my $match;

for my $state ( 1, 0 ) {
    $match = $string =~ m?apple?;
    say(($match == $state) ? "ok" : "not ok");
}

# # Use reset() to allow matching again
# reset();
# $match = $string =~ m?$pattern?;
# print "not " if !$match;
# say "ok # After reset: 'apple' found again";

