#!/bin/bash
# Bash Error Fixture - triggers 5+ issues

# BASH001: Variables without braces
OUTPUT=/tmp/output
HOST=localhost
echo "Saving to $OUTPUT/$HOST/data"
cp file.txt $OUTPUT/$HOST/

# SC2164: cd without error handling
cd /some/directory
cd $HOME/projects

# SC2162: read without -r
echo "Enter name:"
read name

# SC1073: Misplaced quotes
FILENAME="test"txt
