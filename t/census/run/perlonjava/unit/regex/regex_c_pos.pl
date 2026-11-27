use v5.42;

my $str = "hello hello hello";

# Test where /c makes a difference
pos($str) = 6;  # Position at second "hello"

# Without /c - matches from current position
$str =~ /hello/g;  
say((!(pos($str) != 11)) ? "ok" : "not ok");

# With /c - also matches from current pos
pos($str) = 6;
$str =~ /hello/gc;
say((!(pos($str) != 11)) ? "ok" : "not ok");

# Now test with a failed match to see the difference
pos($str) = 6;
$str =~ /xyz/g;  # Fails and resets pos()
say((!(defined pos($str))) ? "ok" : "not ok");

pos($str) = 6;
$str =~ /xyz/gc;  # Fails but keeps pos()
say((!(pos($str) != 6)) ? "ok" : "not ok");

# Test /gc with zero-length match followed by another match at same position
# This is critical for IO::HTML::find_charset_in and similar /gc-based parsers
{
    my $s = "abc";
    pos($s) = 3;  # at end of string
    $s =~ /\G(=?[^\t\n =]*)/gc;  # zero-length match at end
    say pos($s);

    my $r = ($s =~ /\G(=?[^\t\n =]*)/gc);
    say((!$r) ? "ok" : "not ok");
    say pos($s);
}

# Test /g (without /c) resets pos after zero-length match followed by failure
{
    my $s = "abc";
    pos($s) = 3;
    $s =~ /\G(=?[^\t\n =]*)/g;  # zero-length match at end
    say pos($s);

    my $r = ($s =~ /\G(=?[^\t\n =]*)/g);
    say((!$r) ? "ok" : "not ok");
    say((!defined pos($s)) ? "ok" : "not ok");
}

