#!/usr/bin/env python3
"""Test Mega resolver with yt-dlp"""

import sys
sys.path.insert(0, '/home/stecustecu/Documents/samehadaku-addon')

from embed_resolvers import resolve_mega

# Test with a sample Mega embed URL format
test_url = "https://mega.nz/embed/Hq53lQJR#3Ne4UC54BdQgDKuoSMdfKP5rGQLU6xzqaiOtylOgMdQ"

print("Testing Mega resolver...")
print(f"Input URL: {test_url}")
print()

result = resolve_mega(test_url)

if result:
    print(f"\n✓ SUCCESS!")
    print(f"Direct URL: {result[:100]}...")
else:
    print(f"\n❌ FAILED - No direct URL returned")
    print("This could mean:")
    print("  1. yt-dlp doesn't support this Mega URL")
    print("  2. yt-dlp is not installed")
    print("  3. The file requires authentication")
