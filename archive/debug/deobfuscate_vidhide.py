import re

with open('vidhide_embed.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The obfuscated code has a pattern like:
# b o={"1k":"url1","1l":"url2","1t":"url3"};
# We need to find this object

# Look for the object definition
pattern = r'b\s+o\s*=\s*\{([^}]+)\}'
match = re.search(pattern, html)

if match:
    obj_content = match.group(1)
    print("Found object definition:")
    print(obj_content[:500])
    print()
    
    # Extract all key-value pairs
    pairs = re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', obj_content)
    print("Extracted pairs:")
    for key, value in pairs:
        print(f"  {key}: {value[:80]}...")
    
    # Look for URLs
    urls = [value for key, value in pairs if value.startswith('http') or value.startswith('/')]
    print(f"\nFound {len(urls)} URLs:")
    for url in urls:
        print(f"  {url}")
else:
    print("Could not find object definition")
    
# Also try to find sources array
sources_pattern = r'sources\s*:\s*\[([^\]]+)\]'
sources_match = re.search(sources_pattern, html)
if sources_match:
    print("\nFound sources array:")
    print(sources_match.group(1)[:500])
