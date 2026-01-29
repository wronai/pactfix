#!/usr/bin/env python3
"""Generate commit message and update version/changelog for make push"""

import subprocess
import json
import os
from datetime import datetime

def get_staged_files():
    """Get list of staged files"""
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                          capture_output=True, text=True)
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def categorize_file(filename):
    """Categorize file and return appropriate description"""
    if filename.endswith('.py'):
        return f"update {filename}"
    elif filename.endswith(('.js', '.ts', '.tsx')):
        return f"update {filename}"
    elif filename.endswith('.md'):
        return f"docs: update {filename}"
    elif filename == 'Makefile':
        return "build: update Makefile"
    elif filename == 'package.json':
        return "deps: update package.json"
    elif filename == 'Dockerfile':
        return "docker: update Dockerfile"
    elif filename == 'CHANGELOG.md':
        return "chore: update changelog"
    elif filename == 'VERSION':
        return "chore: update version"
    else:
        return f"update {filename}"

def generate_commit_message(files):
    """Generate commit message based on changed files"""
    changes = [categorize_file(f) for f in files if f]
    
    if not changes:
        return None
    
    if len(changes) <= 3:
        return "chore: " + ", ".join(changes)
    else:
        return f"chore: update {len(changes)} files"

def get_current_version():
    """Get current version from VERSION file or default to 1.0.0"""
    try:
        with open('VERSION', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "1.0.0"

def bump_version(version):
    """Bump patch version"""
    parts = version.split('.')
    if len(parts) != 3:
        return "1.0.0"
    patch = int(parts[2]) + 1
    return f"{parts[0]}.{parts[1]}.{patch}"

def update_version_file(new_version):
    """Update VERSION file"""
    with open('VERSION', 'w') as f:
        f.write(new_version + '\n')

def update_changelog(version, files):
    """Update CHANGELOG.md with new version and changes"""
    changes = [categorize_file(f) for f in files if f]
    
    # Read existing changelog
    changelog_path = 'CHANGELOG.md'
    existing_content = ""
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r') as f:
            existing_content = f.read()
    
    # Create new entry
    date_str = datetime.now().strftime('%Y-%m-%d')
    new_entry = f"## [{version}] - {date_str}\n\n"
    for change in changes:
        new_entry += f"- {change}\n"
    new_entry += "\n"
    
    # Write updated changelog
    with open(changelog_path, 'w') as f:
        f.write(new_entry + existing_content)
    
    # Add changelog to staging if it was modified
    subprocess.run(['git', 'add', 'CHANGELOG.md'], capture_output=True)

def main():
    files = get_staged_files()
    
    if not files or files == ['']:
        print("No changes to commit.")
        return
    
    # Generate commit message
    msg = generate_commit_message(files)
    if not msg:
        print("No changes to commit.")
        return
    
    # Update version and changelog
    current_version = get_current_version()
    new_version = bump_version(current_version)
    update_version_file(new_version)
    update_changelog(new_version, files)
    
    # Stage VERSION file
    subprocess.run(['git', 'add', 'VERSION'], capture_output=True)
    
    # Print commit message for makefile to use
    print(msg)

if __name__ == "__main__":
    main()
