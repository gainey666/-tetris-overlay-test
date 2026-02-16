import subprocess
import sys


def run_tests():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Tests failed:\n{proc.stderr}")
    print(proc.stdout)


def main():
    run_tests()


if __name__ == "__main__":
    main()
