use v5.42;

package HLA::Client;

sub new {
    bless {}, shift;
}

sub drop_messages {
    my $self = shift;
    if (my $msgs = delete $self->{msgs}) {
        for my $msg (values %$msgs) {
            $msg->{error} = 1;
        }
    }
    return 1;
}

sub DESTROY {
    $main::destroyed++;
}

package HLA::Message;

sub new {
    my ($class, $parent) = @_;
    bless { parent => $parent }, $class;
}

package main;

$main::destroyed = 0;

{
    my $client = HLA::Client->new;
    $client->{msgs}->{1} = HLA::Message->new($client);
    $client->drop_messages;
}

say $main::destroyed;

