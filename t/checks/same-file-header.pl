# check: ok
# kind: same
# file: data.txt=one\ntwo\n
# file: other.txt=\0101
# A test's files are its headers', in the directory perl is run in (D282): perl
# would print no at all without them.
use v5.42;
for my $name ('data.txt', 'other.txt', 'absent.txt') {
    if (open(my $fh, '<', $name)) {
        my @lines = <$fh>;
        say "$name: ", scalar(@lines);
        close($fh);
    } else {
        say "$name: no";
    }
}
