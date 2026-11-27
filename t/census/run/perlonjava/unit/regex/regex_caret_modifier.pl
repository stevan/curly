use v5.42;

###################
# Perl Caret Modifier Tests

# Test for (?^i:) case insensitive negation
my $string = "Hello HELLO hello";
my $pattern = qr/(?^i:HELLO)/;
my $match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test for (?^i:) with mixed case
$string = "HelloWorld HELLOWORLD";
$pattern = qr/hello(?^i:WORLD)/;
$match = $string =~ $pattern;
say((!($match)) ? "ok" : "not ok");

# Test for multiple modifiers (?^im:)
$string = "Hello\nWorld";
$pattern = qr/(?^im:hello.*world)/;
$match = $string =~ $pattern;
say((!($match)) ? "ok" : "not ok");

# Test for nested modifiers
$string = "TEST test Test";
$pattern = qr/(?^i:test(?^:TEST))/;
$match = $string =~ $pattern;
say((!($match)) ? "ok" : "not ok");

