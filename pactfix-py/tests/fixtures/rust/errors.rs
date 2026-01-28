// Rust Error Fixture - 14 different error types

use std::fs::File;

// RUST001: Using unwrap() in production code
fn read_config() -> String {
    let content = std::fs::read_to_string("config.txt").unwrap();
    content
}

// RUST002: Using expect() without good message
fn open_file() -> File {
    File::open("data.txt").expect("err")
}

// RUST003: clone() usage - potential performance issue
fn process_data(data: Vec<String>) {
    let copy = data.clone();
    println!("{:?}", copy);
}

// RUST004: Using panic! in library code
pub fn library_function(x: i32) {
    if x < 0 {
        panic!("negative value");
    }
}

// RUST005: Unnecessary mut
fn calculate() {
    let mut result = 42;
    println!("{}", result);
}

// RUST006: Using String instead of &str in function parameters
fn greet(name: String) {
    println!("Hello, {}", name);
}

// RUST007: Box<dyn Error> without Send + Sync
fn get_error() -> Box<dyn Error> {
    Box::new(std::io::Error::new(std::io::ErrorKind::Other, "error"))
}

// RUST008: Using println! for logging
fn process() {
    println!("Processing started");
    println!("Step 1 complete");
}

// RUST009: Hardcoded secrets
const API_KEY: &str = "secret-key-12345";
const PASSWORD: &str = "admin123";

// RUST010: Using unsafe without comment
fn dangerous() {
    unsafe {
        let ptr = 0x1234 as *const i32;
        println!("{}", *ptr);
    }
}

// RUST011: Empty match arm
fn handle_result(r: Result<i32, &str>) {
    match r {
        Ok(v) => println!("{}", v),
        Err(_) => {}
    }
}

// RUST012: Using to_string() on string literal
fn get_name() -> String {
    "John".to_string()
}

// RUST013: Redundant closure
fn process_numbers(nums: Vec<i32>) -> Vec<i32> {
    nums.iter().map(|x| double(x)).collect()
}

fn double(x: &i32) -> i32 { x * 2 }

// RUST014: Missing #[must_use] on functions returning Result
pub fn validate(input: &str) -> Result<(), String> {
    if input.is_empty() {
        Err("empty".to_string())
    } else {
        Ok(())
    }
}
