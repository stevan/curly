# The independent review of step 19, T565: which classes perl 5.42 warns of
# as a POSIX class without its brackets ("POSIX syntax [: :] belongs inside
# character classes", "Assuming NOT a POSIX class"), held to the refusal's
# rule: a class with `:`, `=` or `.` twice (an escaped one counting with a
# bare one), or with one of them bare and three letters in a row. Every
# class perl warns of must be one the rule refuses; how many it refuses
# where perl is silent is printed too.
#
#     perl docs/briefs/step19-review/posix-classes.pl
use strict;
use warnings;

sub refused {
    my ($c) = @_;
    my ($raw, $esc) = ('', '');
    while ($c =~ /\G(?:\\(.)|(.))/gs) {
        if (defined $1) { $raw .= '\\'; $esc .= $1; } else { $raw .= $2; }
    }
    for my $d (':', '=', '.') {
        my $bare = () = $raw =~ /\Q$d\E/g;
        my $escaped = () = $esc =~ /\Q$d\E/g;
        return 1 if $bare >= 1 && $bare + $escaped >= 2;
    }
    return $raw =~ /[:=.]/ && $raw =~ /[A-Za-z]{3}/ ? 1 : 0;
}

my @all;
# Every class of up to five of these, bare.
{
    my @al = (':', '=', '.', 'a', 'l', '1', '-', '^', ',', ' ', 'Z', '_');
    my @c = ('');
    for my $len (1 .. 5) { @c = map { my $p = $_; map { $p . $_ } @al } @c; push @all, @c; }
}
# Every class of up to four of these, some escaped.
{
    my @al = (':', '.', '=', 'a', 'l', 'p', 'h', '\\:', '\\.', '\\=', ',', '-', '\\w', '\\d', ' ', '^');
    my @c = ('');
    for my $len (1 .. 4) { @c = map { my $p = $_; map { $p . $_ } @al } @c; push @all, @c; }
}
# The names, whole and cut, with one delimiter or two and something between.
for my $n (qw(alpha alnum ascii blank cntrl digit graph lower print punct space upper word xdigit Alpha ALPHA alpah apha lpha alp al spac pace wo rd ord)) {
    for my $d (':', '=', '.') {
        my $e = "\\$d";
        push @all, "$d$n", "$n$d", "$d $n", "$n $d", "$d^$n", "$d-$n", "$n-$d", "${d}1$n", "$n,$d", "$d,$n", "a-z$d$n", "$d${n}0-9", "0-9$n$d",
            "\\w$d$n", "$n$d\\w", "$d\t$n", "$n\t$d", "$d$n$d", "$d$n ", "_$n$d", "$d${n}_", "x$d$n$d", "$d$n${d}x", "^$d$n$d",
            "$e$n$d", "$d$n$e", "$e$n$e", "$e$n", "$n$e", "$d\\w$n", "$e$n$d$d", "$d$e$n", "$n$d$e", "$d\\ $n", "$d\\-$n", "$d\\^$n";
    }
}

my ($warned, $quiet, $missed, $strict, $dies) = (0, 0, 0, 0, 0);
for my $p (@all) {
    my @w;
    local $SIG{__WARN__} = sub { push @w, $_[0] };
    my $r = eval "no strict; sub { \$_[0] =~ /[$p]/ }";
    if (!$r) { $dies++; next; }
    my $posix = grep { /POSIX|Assuming/ } @w;
    if ($posix) {
        $warned++;
        # (A `[` in a class is refused already.)
        if (!refused($p) && $p !~ /\[/) { $missed++; print "MISSED: [$p]\n"; }
    } else {
        $quiet++;
        $strict++ if refused($p);
    }
}
printf "%d classes: perl does not compile %d, warns of %d as POSIX, is quiet about %d; the rule misses %d of those it warns of, and refuses %d of the quiet\n",
    scalar(@all), $dies, $warned, $quiet, $missed, $strict;
exit($missed ? 1 : 0);
