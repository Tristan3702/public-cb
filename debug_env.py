#!/usr/bin/env python3
"""
Debug script to check environment variable loading
"""

import os
from dotenv import load_dotenv

print("🔍 Environment Variable Debug")
print("=" * 40)

# Clear any existing env vars
if 'SUPABASE_URL' in os.environ:
    del os.environ['SUPABASE_URL']
if 'SUPABASE_KEY' in os.environ:
    del os.environ['SUPABASE_KEY']

print("1. After clearing environment:")
print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"   SUPABASE_KEY: {os.getenv('SUPABASE_KEY')}")

# Load .env file
print("\n2. Loading .env file...")
load_dotenv(override=True)

print("3. After load_dotenv:")
print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"   SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:20] + '...' if os.getenv('SUPABASE_KEY') else 'None'}")

# Check if .env file exists and show its contents
print("\n4. Checking .env file contents:")
try:
    with open('.env', 'r') as f:
        content = f.read()
        print("   .env file exists and contains:")
        for line in content.split('\n'):
            if line.strip() and not line.startswith('#'):
                print(f"   {line}")
except FileNotFoundError:
    print("   .env file not found!")
except Exception as e:
    print(f"   Error reading .env: {e}") 