use v5.42;

###################
# Perl s/// Operator Tests

# Simple substitution
my $string = "Hello World";
my $pattern = qr/World/;
my $replacement = "Universe";
my $substituted = $string =~ s/$pattern/$replacement/r;
say((!($substituted ne "Hello Universe")) ? "ok" : "not ok");

# No substitution
$string = "Hello World";
$pattern = qr/Universe/;
$replacement = "Galaxy";
$substituted = $string =~ s/$pattern/$replacement/r;
say((!($substituted ne "Hello World")) ? "ok" : "not ok");

my $replace_count = $string =~ s/$pattern/$replacement/;
say((defined $replace_count) ? "ok" : "not ok");
say((!$replace_count) ? "ok" : "not ok");
say $replace_count;

# Global substitution
$string = "Hello World World";
$pattern = qr/World/;
$replacement = "Universe";
$substituted = $string =~ s/$pattern/$replacement/gr;
say((!($substituted ne "Hello Universe Universe")) ? "ok" : "not ok");

# Substitution with captured groups
$string = "Hello World";
$pattern = qr/(World)/;
$replacement = "Universe";
$substituted = $string =~ s/$pattern/$replacement/r;
say((!($substituted ne "Hello Universe")) ? "ok" : "not ok");

# Substitution with code
$string = "Hello World";
$pattern = qr/(World)/;
$replacement = sub { return "Universe"; };
$substituted = $string =~ s/$pattern/$replacement->()/er;
say((!($substituted ne "Hello Universe")) ? "ok" : "not ok");

# Substitution with multiple captured groups
$string = "Hello World";
$pattern = qr/(Hello) (World)/;
$substituted = $string =~ s/$pattern/$2, $1/r;
say((!($substituted ne "World, Hello")) ? "ok" : "not ok");

# Substitution with backslash
$string = "Hello World\n";
$pattern = qr/\n/;
$replacement = "\\n";
$substituted = $string =~ s/$pattern/$replacement/r;
say(($substituted eq "Hello World\\n") ? "ok" : "not ok");

###################
# Tests for /r modifier bug

# /r modifier with no match should return original string
$string = "Hello World";
$substituted = $string =~ s/foo/bar/r;
say(($substituted eq "Hello World") ? "ok" : "not ok");

# /r modifier with pattern that doesn't match
$string = "/[[=foo=]]/";
$substituted = $string =~ s/ default_ (on | off) //rx;
say(($substituted eq "/[[=foo=]]/") ? "ok" : "not ok");

# /r modifier preserves original string
$string = "test123";
$substituted = $string =~ s/123/456/r;
say(($string eq "test123") ? "ok" : "not ok");
say(($substituted eq "test456") ? "ok" : "not ok");

# Empty pattern with /r
$string = "test";
$substituted = $string =~ s/nomatch//r;
say(($substituted eq "test") ? "ok" : "not ok");

###################
# Tests for @_ access in s/// replacement

sub test_args_in_replacement {
    my $str = "hello";
    $str =~ s/hello/$_[0]/;
    return $str;
}
say test_args_in_replacement("world");

sub test_args_hash_deref {
    my $str = "AAA::BBB";
    my $class = "AAA";
    $str =~ s/$class/$_[0]->{ns}/;
    return $str;
}
say test_args_hash_deref({ns => "REPLACEMENT"});

sub test_args_with_e_modifier {
    my $str = "hello";
    $str =~ s/hello/$_[0]/e;
    return $str;
}
say test_args_with_e_modifier("world");

sub test_args_with_global {
    my $str = "aaa bbb";
    $str =~ s/\w+/$_[0]/g;
    return $str;
}
say test_args_with_global("X");

