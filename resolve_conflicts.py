#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from ai_conflict_resolver import AIConflictResolver

def find_conflict_files(repo_path='.', file_ext=None):
    """Find files with Git merge conflicts."""
    try:
        cmd = ['git', 'diff', '--name-only', '--diff-filter=U']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path)
        
        if result.returncode != 0:
            print(f"Error finding conflicted files: {result.stderr}")
            return []
        
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        
        if file_ext:
            files = [f for f in files if f.endswith(file_ext)]
            
        return files
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Resolve Git merge conflicts with AI.')
    parser.add_argument('--path', default='.', help='Path to the Git repository')
    parser.add_argument('--extension', default=None, help='Only process files with this extension (e.g. .py)')
    parser.add_argument('--file', help='Process a specific file')
    parser.add_argument('--model', default='anthropic.claude-v2', help='AWS Bedrock model to use')
    parser.add_argument('--auto-commit', action='store_true', help='Automatically commit resolved files')
    
    args = parser.parse_args()
    
    resolver = AIConflictResolver(model_id=args.model)
    resolved_count = 0
    
    if args.file:
        # Resolve a specific file
        if resolver.resolve_file(args.file):
            resolved_count += 1
    else:
        # Find and resolve all conflicted files
        conflict_files = find_conflict_files(args.path, args.extension)
        
        if not conflict_files:
            print("No conflicted files found.")
            return
            
        print(f"Found {len(conflict_files)} files with conflicts")
        
        for file_path in conflict_files:
            full_path = os.path.join(args.path, file_path)
            if resolver.resolve_file(full_path):
                resolved_count += 1
    
    print(f"\nSuccessfully resolved {resolved_count} files")
    
    # Auto-commit if requested
    if args.auto_commit and resolved_count > 0:
        try:
            cmd_add = ['git', 'add'] + conflict_files
            subprocess.run(cmd_add, check=True, cwd=args.path)
            
            cmd_commit = ['git', 'commit', '-m', 'Auto-resolved merge conflicts']
            subprocess.run(cmd_commit, check=True, cwd=args.path)
            
            print("Successfully committed resolved files")
        except subprocess.CalledProcessError as e:
            print(f"Error committing resolved files: {str(e)}")

if __name__ == "__main__":
    main()