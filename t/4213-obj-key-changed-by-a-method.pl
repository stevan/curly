# kind: refused
# perl joins the pieces as it stores, after the key is worked out (T230).
use v5.42;
use experimental 'class';
my $v = "a";
class P { method k { $v = "b"; return "k" } }
my %h;
$h{P->new->k} = $v . "!";
