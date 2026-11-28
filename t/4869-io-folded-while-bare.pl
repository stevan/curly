# kind: refused
# perl folds the test to <STDIN>, and stores each line in its global $_.
use v5.42;
while (1 ? <STDIN> : 0) {
    say "line";
}
