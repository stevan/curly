use v5.42;
if ("foal"=~/(.)(.)(.)(.)/) {
    print join "-", @{^CAPTURE};
}
