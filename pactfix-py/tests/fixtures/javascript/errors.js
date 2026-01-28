// JavaScript Error Fixture - 10+ different error types

// JS001: var usage
var counter = 0;
var name = "test";
var items = [];

// JS002: == instead of ===
if (counter == 0) {
    console.log("zero");
}
if (name == null) {
    console.log("null");
}

// JS003: console.log in production
function calculate() {
    console.log("calculating...");
    console.log("debug:", value);
    return 42;
}

// JS004: eval usage
var result = eval("1 + 2");
var code = eval(userInput);

// Additional common errors:

// Using arguments instead of rest parameters
function oldStyle() {
    var args = arguments;
    return Array.prototype.slice.call(arguments);
}

// Not using strict equality
function compare(a, b) {
    return a == b;
}

// Callback hell
function loadData(callback) {
    getData(function(data) {
        processData(data, function(result) {
            saveData(result, function(saved) {
                callback(saved);
            });
        });
    });
}

// Modifying function parameters
function modify(obj) {
    obj.modified = true;
    return obj;
}

// Using for-in for arrays
var arr = [1, 2, 3];
for (var i in arr) {
    console.log(arr[i]);
}

// Hardcoded secrets
var password = "secret123";
var apiKey = "sk-abcdef123456";
const TOKEN = "bearer_xyz";

// Using document.write
document.write("<h1>Hello</h1>");

// innerHTML with user input
element.innerHTML = userInput;

// setTimeout with string
setTimeout("doSomething()", 1000);
