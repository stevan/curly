use v5.42;

my @absent  = qw(B G J K Q U Y Z);
my %stash_keys = map { $_ => 1 } keys %main::;

for my $letter (@absent) {
    my $key = chr(ord($letter) - ord('A') + 1);
    say((!$stash_keys{$key}) ? "ok" : "not ok");
}

