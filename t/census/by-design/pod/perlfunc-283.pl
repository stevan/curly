use v5.42;
package Bar;
our $bar = 30; # declares $Bar::bar for rest of lexical scope
print $bar;    # prints 30
