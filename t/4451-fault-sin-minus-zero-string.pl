# kind: fault
# perl gives -0 or 0, which atan2 tells apart (T484).
use v5.42;
say sin("0");
say sin("-0");
