use v5.42;
my ($bar);
$bar = "some other value";
print blessed( $bar ) // 'not blessed';    # prints "not blessed"
