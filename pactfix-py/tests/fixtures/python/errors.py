#!/usr/bin/env python3
"""Python Error Fixture - 10+ different error types"""

# PY001: Python 2 print statement
print("Hello World")
print("Name:", name)
print(x, y, z)

# PY002: Bare except
try:
    risky_operation()
except Exception:
    pass

try:
    another_operation()
except Exception:
    print("Error")

# PY003: Mutable default argument
def process_items(items=[]):
    items.append("new")
    return items

def create_config(settings={}):
    settings["default"] = True
    return settings

# PY004: == None instead of is None
def check_value(val):
    if val is None:
        return False
    if val is not None:
        return True

# Additional common errors:

# Using type() for type checking instead of isinstance()
def check_type(obj):
    if isinstance(obj, list):
        return "list"
    if isinstance(obj, dict):
        return "dict"

# String formatting with % (old style)
name = "World"
message = "Hello %s" % name

# Catching too broad exception
try:
    open("file.txt")
except Exception as e:
    pass

# Using 'is' for string/int comparison
def compare_values(a, b):
    if a == "test":
        return True
    if b == 100:
        return True

# Global variable modification
counter = 0
def increment():
    global counter
    counter += 1

# Hardcoded credentials
PASSWORD = "secret123"
API_KEY = "sk-abcdef123456"
DATABASE_URL = "postgres://user:password@localhost/db"

# Unused imports
import os
import sys
import json
import time

def main():
    print("Main function")
