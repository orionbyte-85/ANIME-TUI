import subprocess

url = "https://v1.samehadaku.how/one-piece-fan-letter-episode-1/"
cmd = f'curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" "{url}" > curl_output.html'

print(f"Running: {cmd}")
subprocess.call(cmd, shell=True)

print("Done. Checking file size...")
subprocess.call("ls -l curl_output.html", shell=True)

print("Checking for #server div...")
subprocess.call("grep -A 20 'id=\"server\"' curl_output.html", shell=True)
