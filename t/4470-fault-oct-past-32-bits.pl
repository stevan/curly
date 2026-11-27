# kind: fault
# perl warns: Octal number > 037777777777 non-portable (T473).
use v5.42;
say oct("37777777777");
say oct("40000000000");
