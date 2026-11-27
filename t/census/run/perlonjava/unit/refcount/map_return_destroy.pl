use v5.42;

{
    package MapReturnDestroy;
    our $counter = 0;
    sub new {
        my $class = shift;
        my $self = bless {}, $class;
        $counter++;
        return $self;
    }
    sub DESTROY {
        $counter-- if $counter > 0;
    }
}

my @objs = map { MapReturnDestroy->new } 1 .. 3;
say $MapReturnDestroy::counter;

@objs = ();
say $MapReturnDestroy::counter;

