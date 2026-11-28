use v5.42;

sub Pending;

my $pending = 'main::Pending';
my $coderef = \&{$pending};

say((defined($coderef)) ? "ok" : "not ok");
say((!defined(&{$pending})) ? "ok" : "not ok");
say((exists(&{$pending})) ? "ok" : "not ok");

{
    package ParentForDefinedDynamic;
    sub inherited { 'inherited' }

    package ChildForDefinedDynamic;
    our @ISA = ('ParentForDefinedDynamic');
}

my $inherited = 'ChildForDefinedDynamic::inherited';
say((ChildForDefinedDynamic->can('inherited')) ? "ok" : "not ok");
say((!defined(&{$inherited})) ? "ok" : "not ok");

{
    package ParentForMakeMakerDynamic;
    sub makemakerdflt_target { 'target' }

    package MYForMakeMakerDynamic;
    our @ISA = ('ParentForMakeMakerDynamic');
}

say((MYForMakeMakerDynamic->can('makemakerdflt_target')) ? "ok" : "not ok");
say((!defined(&{'MYForMakeMakerDynamic::makemakerdflt'})) ? "ok" : "not ok");

