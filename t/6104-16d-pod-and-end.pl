# POD where a statement may begin, to =cut or the end; __END__ (D255).
use v5.42;
say 1;

=head1 NAME

pod-and-end: say ? not perl

=cut

say 2;
=pod
=cutting is not the end
say "no";
=cut back to code
say 3;
if (1) {

=begin comment

inside a block

=end comment

=cut

    say 4;
}
=cut
this is POD too, to the next =cut
=cut
say 5;
__END__
say 6; not perl ( {
