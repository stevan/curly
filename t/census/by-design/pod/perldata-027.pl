use v5.42;
my (@name);
@name = qw(Larry Curly Moe);
local $" = " and ";
print "My favorites were @{name[1,2]}.\n";
