use v5.42;

# Test positive infinity
my $x = "Inf";
say((!((0 + $x) != "Inf")) ? "ok" : "not ok");
say((!((-$x) != "-Inf")) ? "ok" : "not ok");
say((!((0 - $x) != "-Inf")) ? "ok" : "not ok");

# Test negative infinity
$x = "-Inf";
say((!((0 + $x) != "-Inf")) ? "ok" : "not ok");

# Test NaN (Not a Number)
$x = "NaN";
say((!((0 + $x) == (0 + $x))) ? "ok" : "not ok");

# Test case-insensitivity for Inf
$x = "inf";
say((!((0 + $x) != "Inf")) ? "ok" : "not ok");

# Test case-insensitivity for -Inf
$x = "-inf";
say((!((0 + $x) != "-Inf")) ? "ok" : "not ok");

# Test case-insensitivity for NaN
$x = "nan";
say((!((0 + $x) == (0 + $x))) ? "ok" : "not ok");

