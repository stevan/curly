# kind: warns
# stdin: only\n
# A warn names the handle too, once a line has been read (T516).
use v5.42;
say eof(STDIN) ? "end" : "more";
warn "not yet";
my $l = <STDIN>;
warn "read ", length($l);
say "done";
