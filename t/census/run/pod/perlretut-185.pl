use v5.42;
my ($x, $z0, $z1);
$x = "1101010010001000001";
$z0 = ''; $z1 = '0';   # initial conditions
print "It is a Fibonacci sequence\n"
    if $x =~ /^1         # match an initial '1'
                (?:
                   ((??{ $z0 })) # match some '0'
                   1             # and then a '1'
                   (?{ $z0 = $z1; $z1 .= $^N; })
                )+   # repeat as needed
              $      # that is all there is
             /x;
printf "Largest sequence matched was %d\n", length($z1)-length($z0);
