<?php
// PHP Error Fixture - 10+ different error types

// PHP001: Unvalidated input
$username = $_GET['username'];
$email = $_POST['email'];
$data = $_REQUEST['data'];
$session = $_COOKIE['session'];

// PHP002: == instead of === for comparisons
if ($value == null) {
    echo "null";
}
if ($result == false) {
    echo "false";
}

// PHP003: Deprecated mysql_* functions
$conn = mysql_connect("localhost", "user", "pass");
$result = mysql_query("SELECT * FROM users");
$row = mysql_fetch_array($result);

// PHP004: extract() is dangerous
$data = $_POST;
extract($data);
extract($_GET);

// PHP005: Error suppression operator @
@file_get_contents("missing.txt");
@mysql_connect("localhost", "user", "pass");
$result = @unserialize($data);

// PHP006: Short tags
<? echo "Short tag"; ?>
<?= $variable ?>

// Additional common errors:

// SQL injection vulnerability
$id = $_GET['id'];
$query = "SELECT * FROM users WHERE id = $id";
mysql_query($query);

// XSS vulnerability
echo $_GET['name'];
echo "<div>" . $_POST['content'] . "</div>";

// Hardcoded credentials
$password = "secret123";
$api_key = "sk-abcdef123456";
define('DB_PASSWORD', 'admin123');

// Using eval
eval($_GET['code']);
$result = eval('return ' . $expression . ';');

// Insecure file operations
include($_GET['page']);
require($_POST['module']);

// Weak cryptography
$hash = md5($password);
$encrypted = base64_encode($data);
?>
