import similarity_walker
import subprocess


@similarity_walker.duration
def check_time(x):
    subprocess.check_call(["python", "similarity_walker.py", ".", "--size", str(x)])


if __name__ == "__main__":
    for _ in range(20):
        l, r = 0, 1 * 10 ** 6
        while l < r - 10000:
            m1 = l + (r - l) // 3
            m2 = r - (r - l) // 3
            if check_time(m1) > check_time(m2):
                l = m1
            else:
                r = m2
        with open("tests.txt", "a") as file:
            file.write(str(l) + ' ')
