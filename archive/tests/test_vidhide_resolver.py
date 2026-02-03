from embed_resolvers import resolve_vidhide

# Test with the URL from the error
url = "https://odvidhide.com/embed/n87x8jeevpnp"

print(f"Testing Vidhide resolver...")
print(f"URL: {url}")
print()

result = resolve_vidhide(url)

if result:
    print(f"\n✅ Success!")
    print(f"Direct URL: {result}")
else:
    print(f"\n❌ Failed to extract video URL")
