#!/usr/bin/env python3
"""
Quick status checker - see how many plans have been generated
"""
import glob
import json

review_files = glob.glob('review_*.json')
print(f"Plans generated so far: {len(review_files)}/10")

if review_files:
    print("\nCompleted tests:")
    for f in sorted(review_files):
        with open(f) as file:
            data = json.load(file)
            print(f"  ✅ {data['test_name']}")
