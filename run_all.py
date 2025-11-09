import subprocess

# List of scripts to run sequentially
scripts = [
    "archive_scraper.py",
    "product_scraper.py",
    "profile_scraper.py"
]

for script in scripts:
    print(f"\n=== Running {script} ===\n")
    subprocess.run(["python", script], check=True)
