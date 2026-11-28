# By hand, with perl's answers (the independent review of step 21b; T698, D287): perl makes the handle, or takes
# the one the variable holds, before the file's name is worked out, so a name that reads the variable finds a handle.
# file: in.txt=first\nsecond\n
# file: other.txt=other\n
# file: second=the file named by a line\n
use v5.42;
my $fh;
sub pick() {
    return defined($fh) ? 'in.txt' : 'other.txt';
}
open($fh, '<', pick()) or die "no\n";
my $l = <$fh>;
print $l;
close($fh);

my $g;
open($g, '<', $g ? 'in.txt' : 'other.txt') or die "no\n";
$l = <$g>;
print $l;

my $h;
my $kind = sub { return ref($h) };
open($h, '<', $kind->() eq 'GLOB' ? 'in.txt' : 'other.txt') or die "no\n";
$l = <$h>;
print $l;

# A my's too, to a sub written below it.
open(my $late, '<', below()) or die "no\n";
$l = <$late>;
print $l;
sub below() {
    return defined($late) ? 'in.txt' : 'other.txt';
}

# The name may read from the handle, and close it: the variable holds it still.
open(my $two, '<', 'in.txt') or die "no\n";
sub named_inside() {
    my $skip = <$two>;
    my $name = <$two>;
    chomp($name);
    close($two);
    return $name;
}
open($two, '<', named_inside()) or die "no\n";
$l = <$two>;
print $l;

# An outer variable of the handle's name is the one the name reads.
my $name = 'other.txt';
{
    open(my $name, '<', $name) or die "no\n";
    $l = <$name>;
    print $l;
}
