package Devel::PatchPerl::Plugin::CurlyRoles;

# A Devel::PatchPerl plugin that applies roles-5.42.0.patch, so that
# perlbrew or plenv can build the roles perl (D181, D186):
#
#   PERL5LIB=/path/to/curly/tools/perl-roles/lib \
#   PERL5_PATCHPERL_PLUGIN=CurlyRoles \
#   perlbrew install perl-5.42.0 --as perl-5.42.0-roles
#
# Devel::PatchPerl only warns when a plugin dies, so a failure here
# leaves a plain 5.42.0 under the roles name: check the perl it built
# (README.md, "Is it the roles perl?").

use strict;
use warnings;

use Cwd ();
use File::Basename ();
use File::Spec;

sub patchperl {
    my ($class, %args) = @_;
    my $version = $args{version} || '';
    die "CurlyRoles: the patch is for perl 5.42.0, not '$version'\n"
        unless $version eq '5.42.0';

    my $here = File::Basename::dirname(Cwd::abs_path(__FILE__));
    my $patch = $ENV{CURLY_ROLES_PATCH}
        || File::Spec->catfile($here, (File::Spec->updir) x 4, 'roles-5.42.0.patch');
    die "CurlyRoles: no patch at $patch\n" unless -r $patch;

    # The patch goes to patch(1) on its stdin, from here, and no shell
    # sees its path.
    my $exe = $args{patchexe} || 'patch';
    open my $in, '<', $patch or die "CurlyRoles: can't read $patch: $!\n";
    open my $to, '|-', $exe, '-p1', '-s'
        or die "CurlyRoles: can't run $exe: $!\n";
    print {$to} $_ while <$in>;
    close $in;
    close $to or die "CurlyRoles: '$exe -p1' failed on $patch\n";
    print "CurlyRoles: applied $patch\n";
    return 1;
}

1;
