#!/usr/bin/env python3
"""
Watch test progress in real-time
"""
import time
import glob
import os

print("🔄 Watching test progress... (Press Ctrl+C to stop)\n")

last_count = 0
while True:
    try:
        review_files = glob.glob('review_*.json')
        count = len(review_files)
        
        if count != last_count:
            print(f"📊 Progress: {count}/10 tests completed")
            
            if count > last_count:
                # Show newly completed tests
                for f in sorted(review_files)[-1:]:
                    test_name = f.replace('review_', '').replace('.json', '')
                    print(f"   ✅ {test_name}")
            
            last_count = count
        
        if count >= 10:
            print("\n✅ All tests complete!")
            print("\nRun: python3 review_plans.py")
            break
        
        time.sleep(5)
        
    except KeyboardInterrupt:
        print(f"\n\nStopped. Current progress: {count}/10")
        break
