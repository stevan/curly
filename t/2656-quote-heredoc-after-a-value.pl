# kind: refused
# perl takes $x for a file handle: Can't use string ("1") as a symbol ref. Since step 22 << after a value is the left shift, and this is the file-handle guess (T478).
use v5.42;
my $x = 1;
say $x <<EOT;
EOT
