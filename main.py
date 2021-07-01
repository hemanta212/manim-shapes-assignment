import os
import subprocess

def main():
    cmd = "manim render triangle_gen.py --quality h --silent -v ERROR -s"
    if not os.path.exists('images'):
        os.mkdir('images')

    print("::Processing...")
    subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, check=True)
    print("::Reading triangle.ini...")
    print("::Output Generated at: ./images folder")


if __name__ == '__main__':
    main()
