use v5.42;

my $str = "aaa bbb aaa";

# Test 1: Normal capturing without /n
$str =~ /(aaa)/;
say((!($1 ne "aaa")) ? "ok" : "not ok");

# Test 2: Disable capturing with (?n) inline
$str =~ /(?n)(aaa)/;
say((!(defined $1)) ? "ok" : "not ok");

# Test 3: Disable capturing with (?n:...) group syntax
$str =~ /(?n:(aaa))/;
say((!(defined $1)) ? "ok" : "not ok");

# Test 4: Mixed capturing - outside enabled, inside disabled
$str =~ /((?n:aaa) bbb)/;
print "not " unless ($1 eq "aaa bbb");
say((!(defined $2)) ? "ok" : "not ok");

# Test 5: Turn off /n with (?^)
$str =~ /(?n)(aaa) (?^)(bbb)/;
print "not " if defined $2;
say((!($1 ne "bbb")) ? "ok" : "not ok");

# Test 6: Multiple groups with /n
$str =~ /(?n)(aaa) (bbb) (aaa)/;
say((!(defined $1 || defined $2 || defined $3)) ? "ok" : "not ok");

# Test 7: Nested groups with /n
$str =~ /(?n:(aaa (bbb) aaa))/;
say((!(defined $1 || defined $2)) ? "ok" : "not ok");

