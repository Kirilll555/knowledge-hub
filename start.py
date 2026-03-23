import subprocess
import sys

def run(cmd):
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\nStopped by user")
        sys.exit(0)

def main():
    python = sys.executable

    print("Applying migrations...")
    run(f"{python} manage.py migrate")

    print("Starting server...")
    run(f"{python} manage.py runserver")

if __name__ == "__main__":
    main()
