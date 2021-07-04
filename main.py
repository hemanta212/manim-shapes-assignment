import os
import subprocess


def main():
    cmd = "manim render triangle.py --quality h --silent -v ERROR -s"
    if not os.path.exists("images"):
        os.mkdir("images")

    print("::Processing...")
    print("::Reading triangle.ini...")
    subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, check=True)
    print("::Output Generated at: ./images folder")


if __name__ == "__main__":
    main()
