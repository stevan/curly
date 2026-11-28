# __LINE__, the line of the token itself, and __FILE__, the path perl was given (D255).
use v5.42;
say __LINE__;
say "a",
  __LINE__,
  "b";
say __LINE__
  + 1;
my $l = 0 +
  __LINE__;
say $l;
say __LINE__ . __LINE__;
my %h = (__LINE__ => 1);
say sort keys %h;
say __FILE__;
my $s = "__LINE__ __FILE__";
say $s;
sub where() {
    return __LINE__;
}
say where();
