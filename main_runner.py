import subprocess
import sys

def run_scrapy_spider():
    print("Running Scrapy spider...")
    subprocess.run([sys.executable, "-m", "scrapy", "crawl", "ad_spider"], check=True)

def run_fetch():
    print("Running fetch.py...")
    subprocess.run([sys.executable, "fetch.py"], check=True)

def run_analyse():
    print("Running analyse.py...")
    subprocess.run([sys.executable, "analyse.py"], check=True)

if __name__ == "__main__":
    try:
        run_scrapy_spider()
        run_fetch()
        run_analyse()
        print("All scripts executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during execution: {e}")