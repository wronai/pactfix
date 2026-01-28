// TypeScript Error Fixture - 14 different error types

// TS001: any type usage
function processData(data: any): any {
    return data;
}

// TS002: Non-null assertion overuse
const element = document.getElementById("test")!.innerHTML;

// TS003: var instead of let/const
var counter = 0;
var name = "test";

// TS004: == instead of ===
if (counter == 0) {
    console.log("zero");
}

// TS005: console.log in production
function calculate() {
    console.log("calculating...");
    return 42;
}

// TS006: eval usage
const result = eval("1 + 2");

// TS007: @ts-ignore without explanation
// @ts-ignore
const bad: number = "string";

// TS008: Empty interface
interface EmptyInterface {}

// TS009: Function without return type
function getData(id) {
    return fetch(`/api/${id}`);
}

// TS010: async function without await
async function loadData() {
    return "data";
}

// TS011: Promise constructor anti-pattern
async function fetchData() {
    return new Promise((resolve) => {
        resolve("data");
    });
}

// TS012: Object type usage
function process(obj: Object): Object {
    return obj;
}

// TS013: String/Number/Boolean wrapper types
function format(value: String): Number {
    return parseInt(value as string);
}

// TS014: Potentially unused import
import { unusedFunction } from './utils';
