use v5.42;
my ($str);
$str = formline <<'END', 1,2,3;
@<<<  @|||  @>>>
END

print "Wow, I just stored '$^A' in the accumulator!\n";
