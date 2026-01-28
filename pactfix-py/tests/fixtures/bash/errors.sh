#!/bin/bash
# Bash Error Fixture - 10+ different error types

# BASH001: Variables without braces
OUTPUT=/tmp/output
HOST=localhost
echo "Saving to $OUTPUT/$HOST/data"
cp file.txt $OUTPUT/$HOST/

# SC2164: cd without error handling
cd /some/directory
cd "$HOME/projects"

# SC2162: read without -r
echo "Enter name:"
read name
read -p "Enter value: " value

# SC1073: Misplaced quotes
FILENAME="test"txt
CONFIG="path"/to/config

# More variable issues
USER_DIR=$HOME/users/$USERNAME
LOG_FILE=$OUTPUT/logs/$DATE.log

# Missing error handling on critical commands
mkdir $OUTPUT
rm -rf $TEMP_DIR

# Unquoted variables with spaces
FILES=$INPUT_DIR/*
for f in $FILES; do
    process $f
done

# SC2086: Double quote to prevent globbing
echo $USER_INPUT
cat $CONFIG_FILE

# SC2046: Quote command substitutions
for file in $(find . -name "*.txt"); do
    echo $file
done

# SC2006: Use $() instead of backticks
DATE=`date +%Y-%m-%d`
VERSION=`cat VERSION`

# Hardcoded secrets
PASSWORD="secret123"
API_KEY="sk-abcdef123456"
export DATABASE_PASSWORD=admin123
