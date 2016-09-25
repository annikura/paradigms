import argparse
import time

import funcs


def duration(function):
    def wrapper(x):
        tin = time.time()
        function(x)
        return time.time() - tin

    return wrapper


# @duration
def main(sz):
    parser = argparse.ArgumentParser(
             description='Detects similar files in a given directory')
    parser.add_argument('dir', help='directory path')
    parser.add_argument('--size', '-s', type=int, default=512,
                        help='size of a block to read files by')

    args = parser.parse_args()
    if sz:
        args.size = sz
    for fls in funcs.find_similar(funcs.get_file_names(args.dir), args.size):
        print(':'.join(fls))


if __name__ == "__main__":
    main(None)
