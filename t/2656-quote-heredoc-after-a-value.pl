# kind: fault
# perl takes $x for a file handle: Can't use string ("1") as a symbol ref. Since step 21b so does the language (D278), and $x holds none.
use v5.42;
my $x = 1;
say $x <<EOT;
EOT
