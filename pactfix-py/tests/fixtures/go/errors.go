// Go Error Fixture - 14 different error types
package main

import (
    "database/sql"
    "errors"
    "fmt"
    "time"
)

// GO001: Unchecked error
func readFile() {
    file, err := os.Open("file.txt")
    // Missing error check!
    fmt.Println(file)
}

// GO002: Using panic in library code
func LibraryFunction() {
    panic("something went wrong")
}

// GO003: Empty error message
func validateInput(s string) error {
    if s == "" {
        return errors.New("")
    }
    return nil
}

// GO004: fmt.Sprintf without format args
func getMessage() string {
    return fmt.Sprintf("Hello World")
}

// GO005: Goroutine without sync
func startWorker() {
    go func() {
        fmt.Println("working")
    }()
}

// GO006: This would be a slice comparison issue

// GO007: Defer in loop
func processFiles(files []string) {
    for _, f := range files {
        file, _ := os.Open(f)
        defer file.Close()
    }
}

// GO008: Using time.Sleep in production
func waitAndProcess() {
    time.Sleep(5 * time.Second)
    fmt.Println("done")
}

// GO009: Hardcoded credentials
const password = "super_secret_123"
const apiKey = "sk-1234567890abcdef"

// GO010: SQL injection risk
func getUser(db *sql.DB, id string) {
    query := "SELECT * FROM users WHERE id = " + id
    db.Query(query)
}

// GO011: Context as struct field
type Service struct {
    ctx context.Context
}

// GO012: Using init() function
func init() {
    fmt.Println("initializing")
}

// GO013: Missing package comment - this file doesn't have proper package doc

// GO014: Using interface{} instead of any
func process(data interface{}) interface{} {
    return data
}
