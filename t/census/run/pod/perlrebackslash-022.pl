use v5.42;
while ("cat dog" =~ /(\w+)/g) {
    print $1;           # Prints 'catdog'
}
while ("cat dog" =~ /\G(\w+)/g) {
    print $1;           # Prints 'cat'
}
