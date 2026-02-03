#!/usr/bin/env python3
"""Test MPV header format"""
import subprocess

url = "https://vidcache.net:8161/a20251127BBmsx5nRq6g/video.mp4"

# Test different header formats
formats = [
    # Format 1: Comma-separated (current)
    ["mpv", "--http-header-fields=User-Agent: Mozilla/5.0,Referer: https://www.yourupload.com/", url],
    
    # Format 2: Multiple --http-header-fields
    ["mpv", "--http-header-fields=User-Agent: Mozilla/5.0", "--http-header-fields=Referer: https://www.yourupload.com/", url],
    
    # Format 3: Single string with newlines
    ["mpv", "--http-header-fields=User-Agent: Mozilla/5.0\r\nReferer: https://www.yourupload.com/", url],
]

print("Testing MPV header formats...\n")

for i, cmd in enumerate(formats):
    print(f"--- Format {i+1} ---")
    print(f"Command: {' '.join(cmd[:3])}")
    print("Testing for 5 seconds...")
    
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait(timeout=5)
        print(f"Exit code: {proc.returncode}")
        if proc.returncode == 0:
            print("✅ SUCCESS!")
            break
    except subprocess.TimeoutExpired:
        proc.kill()
        print("✅ Video started playing (timeout = success)")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")
