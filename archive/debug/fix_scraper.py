import re

file_path = '/home/stecustecu/Documents/samehadaku-addon/scraper.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Remove the first 7 lines (corrupted/duplicate start)
# The file content showed lines 1-7 were garbage/duplicate start
# 1: import re
# ...
# 7:         "User-Agent": ... (incomplete)
# 8:     import re (indented)

# So we keep from line 8 onwards (index 7)
new_lines = lines[7:]

# Dedent
# Check indentation of the first line (which should be '    import re')
first_line = new_lines[0]
indent = len(first_line) - len(first_line.lstrip())
print(f"Detected indent: {indent}")

final_lines = []
for line in new_lines:
    if line.strip() == "":
        final_lines.append("\n")
    else:
        # Remove 'indent' number of spaces from start
        if line.startswith(" " * indent):
            final_lines.append(line[indent:])
        else:
            # Should not happen if consistent, but just in case lstrip or keep
            final_lines.append(line.lstrip())

with open(file_path, 'w') as f:
    f.writelines(final_lines)

print("Fixed scraper.py")
