use v5.42;
package Foo;
our $bar;      # declares $Foo::bar for rest of lexical scope
$bar = 20;

package Bar;
print $bar;    # prints 20, as it refers to $Foo::bar
