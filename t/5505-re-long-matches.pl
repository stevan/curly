# Matches over strings of megabytes, which step 19 first faulted at for
# their length alone (T568): the limit grows with the string now (D244),
# and a run is one frame of the matcher's stack however long it is (D241).
# Lengths and counts are printed, not the strings.
use v5.42;
my $as = "a" x 3000000;
say $as =~ /^a*$/ ? 1 : 0;
say $as =~ /^a+$/ ? 1 : 0;
say $as =~ /a$/ ? 1 : 0;
say $as =~ /^.*$/ ? 1 : 0;
say $as =~ /^[^b]*$/ ? 1 : 0;
say $as =~ /^\w+\z/ ? 1 : 0;
say $as =~ /b/ ? 1 : 0;
say $as !~ /^a*$/ ? 1 : 0;
my ($all) = $as =~ /^(a*)$/;
say length($all);
my ($most, $last) = $as =~ /^(.*)(a{5})$/;
say length($most), " ", length($last);
my ($few, $rest) = $as =~ /^(a*?)(a{3000}a*)$/;
say length($few), " ", length($rest);
my ($lazy) = $as =~ /^(.+?)$/;
say length($lazy);
my $hay = ("hay " x 700000) . "needle" . (" hay" x 10);
say $hay =~ /needle/ ? 1 : 0;
say $hay =~ /needles/ ? 1 : 0;
say $hay =~ /n[e]+dle\b/ ? 1 : 0;
say $hay =~ /^needle/ ? 1 : 0;
say $hay =~ /^needle/m ? 1 : 0;
say $hay =~ /yah/ ? 1 : 0;
say $hay =~ /hay hay$/ ? 1 : 0;
my ($before, $after) = $hay =~ /^(.*)needle(.*)$/;
say length($before), " ", length($after);
my ($word) = $hay =~ /(\w{5,})/;
say $word;
my ($tail) = $hay =~ /needle((?: hay)+)$/;
say length($tail);
my $lines = ("line\n" x 400000) . "end";
say $lines =~ /^end$/m ? 1 : 0;
say $lines =~ /^end$/ ? 1 : 0;
say $lines =~ /\Aline\n(?:line\n)*end\z/ ? 1 : 0;
my ($one) = $lines =~ /^(.*)$/m;
say length($one);
my ($whole) = $lines =~ /^(.*)$/s;
say length($whole);
