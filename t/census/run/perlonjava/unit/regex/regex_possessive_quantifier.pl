use v5.42;

###################
# Perl Possessive Quantifier Tests

# Test simple *+ (possessive star)
my $string = "aaaaab";
my $pattern = qr/a*+b/;  # Matches 'aaaaab' - consumes all 'a's and the 'b'
my $match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Compare with greedy * for demonstration
$string = "aaaaab";
$pattern = qr/a*ab/;  # Matches 'aaaaab' - backtracks to match final 'ab'
$match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test where possessive *+ fails but greedy * succeeds
$string = "aaaaab";
$pattern = qr/a*+ab/;  # Fails - possessive *+ takes all 'a's, leaving none for 'ab'
$match = $string =~ $pattern;
say((!$match) ? "ok" : "not ok");

# Test ++ (possessive plus)
$string = "aaaaa";
$pattern = qr/a++/;  # Matches 'aaaaa' - takes all 'a's
$match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test ?+ (possessive optional)
$string = "ab";
$pattern = qr/a?+b/;  # Matches 'ab'
$match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test where possessive ?+ affects matching
$string = "b";
$pattern = qr/a?+a/;  # Fails - possessive ?+ commits to taking or not taking 'a'
$match = $string =~ $pattern;
say((!$match) ? "ok" : "not ok");

# Test {n,m}+ (possessive range)
$string = "aaaaab";
$pattern = qr/a{2,4}+b/;  # Matches 'aaaaab' - takes maximum 4 'a's allowed
$match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test where possessive {n,m}+ fails but greedy {n,m} succeeds
$string = "aaaaa";
$pattern = qr/a{2,4}+aa/;  # Fails - possessive takes max 4 'a's, not enough left for 'aa'
$match = $string =~ $pattern;
say((!$match) ? "ok" : "not ok");

# Test with word boundaries
$string = "wordword";
$pattern = qr/\b\w++\b/;  # Matches 'wordword' as a single word
$match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test in a complex pattern
$string = "The quick brown fox";
$pattern = qr/\b\w++\s++\w++\s/;  # Matches "quick " using possessive quantifiers
$match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Test with capturing groups
$string = "aaabbbccc";
$pattern = qr/(a++)(b++)(c++)/;  # Matches and captures each group possessively
$match = $string =~ $pattern;
say(($match) ? "ok" : "not ok");

# Compare possessive vs non-possessive in a longer string
$string = "The quick brown fox jumps over the lazy dog";
$pattern = qr/.*+fox/;  # Fails - possessive .* takes everything
$match = $string =~ $pattern;
say((!$match) ? "ok" : "not ok");

