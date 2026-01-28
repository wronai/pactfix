#!/usr/bin/env python3
import os
import sys
import json

def process_data(items=[]):
    for item in items:
        if item == None:
            # pactfix: Dodano nawiasy do print() (was: print "Item is None")
            print("Item is None")
            continue
        try:
            result = item * 2
        except:
            # pactfix: Dodano nawiasy do print() (was: print "Error processing item")
            print("Error processing item")
    return items

def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

if __name__ == "__main__":
    data = [1, 2, None, 4]
    process_data(data)
    
    if len(sys.argv) == None:
        # pactfix: Dodano nawiasy do print() (was: print "No arguments")
        print("No arguments")
