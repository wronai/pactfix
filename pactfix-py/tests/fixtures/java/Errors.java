// Java Error Fixture - 15 different error types
package com.example;

import java.io.*;
import java.sql.*;
import java.util.*;

public class Errors {
    
    // JAVA001: Using == for String comparison
    public boolean checkName(String name) {
        return name == "admin";
    }
    
    // JAVA002: Catching generic Exception
    public void readFile() {
        try {
            FileInputStream fis = new FileInputStream("test.txt");
        } catch (Exception e) {
            // too broad
        }
    }
    
    // JAVA003: Empty catch block
    public void processData() {
        try {
            int x = 1 / 0;
        } catch (ArithmeticException e) {
        }
    }
    
    // JAVA004: Using System.out.println for logging
    public void doWork() {
        System.out.println("Starting work...");
        System.err.println("Error occurred");
    }
    
    // JAVA005: Hardcoded credentials
    private String password = "secret123";
    private String apiKey = "sk-abcdef123456";
    
    // JAVA006: Using raw types
    public void processList() {
        List items = new ArrayList();
        Map data = new HashMap();
    }
    
    // JAVA007: Public fields
    public String username;
    public int age;
    
    // JAVA008: Missing @Override annotation
    public boolean equals(Object obj) {
        return super.equals(obj);
    }
    
    public int hashCode() {
        return super.hashCode();
    }
    
    // JAVA009: Using + for String concatenation in loop
    public String buildString(List<String> parts) {
        String result = "";
        for (String part : parts) {
            result = result + part;
        }
        return result;
    }
    
    // JAVA010: Not closing resources
    public void readData() throws IOException {
        FileInputStream fis = new FileInputStream("data.txt");
        BufferedReader reader = new BufferedReader(new InputStreamReader(fis));
        String line = reader.readLine();
    }
    
    // JAVA011: Using Thread.sleep in main thread
    public void waitAndContinue() throws InterruptedException {
        Thread.sleep(5000);
    }
    
    // JAVA012: Synchronized on method level
    public synchronized void updateCounter() {
        // ...
    }
    
    // JAVA013: Using Date instead of LocalDate
    public void logTime() {
        Date now = new Date();
        System.out.println(now);
    }
    
    // JAVA014: SQL injection risk
    public void getUser(Connection conn, String userId) throws SQLException {
        String query = "SELECT * FROM users WHERE id = " + userId;
        Statement stmt = conn.createStatement();
        stmt.executeQuery(query);
    }
    
    // JAVA015: NullPointerException risk
    public void process(String input) {
        String value = null;
        int length = value.length();
    }
}
