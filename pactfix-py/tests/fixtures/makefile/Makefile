# Makefile Error Fixture - 14 different error types

# MAKE001: Spaces instead of tabs (intentional error - using spaces)
all:
    echo "Building..."

# MAKE003: Missing .PHONY for standard targets
build:
	gcc -o main main.c

test:
	./run_tests.sh

install:
	cp main /usr/local/bin/

# MAKE004: Hardcoded paths
deploy:
	cp main /home/user/projects/app/bin/
	scp main /usr/local/specific/path

# MAKE005: cd without && 
change_dir:
	cd src
	make

# MAKE006: Using $(shell echo)
VERSION := $(shell echo "1.0.0")
NAME := $(shell cat name.txt)

# MAKE007: Recursive make without $(MAKE)
submake:
	make -C subdir
	make clean

# MAKE011: rm without -f
clean:
	rm *.o
	rm main

# MAKE012: (checking for missing clean - already have one above)

# MAKE013: Using $(wildcard) in prerequisites  
sources: $(wildcard *.c)
	gcc -o out $^

# MAKE014: Double-colon rules
config::
	echo "First config"

config::
	echo "Second config"

# Missing .PHONY declaration for all, build, test, install, clean
