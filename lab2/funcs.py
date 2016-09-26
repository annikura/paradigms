import hashlib
import os
from collections import defaultdict


def take_hash(filename, read_length=10 ** 5):
    """
    Takes a file and returns it's hash, counted by blocks of read_length
    """
    file_hash = hashlib.sha1()
    with open(filename, "rb") as file:
        for s in iter(lambda: file.read(read_length), ''):
            file_hash.update(s)
    return file_hash.digest()


def find_similar(files, read_length=10 ** 5):
    """
    Takes a list of files and returns lists of equal by content
    """
    eqls = defaultdict(list)
    for file in files:
        eqls[take_hash(file, read_length)].append(file)
    return [eqls[key] for key in eqls if len(eqls[key]) > 1]


def filter_files(files):
    return filter(lambda x: x[0] not in ['.', '~'], files)


def get_file_names(directory, check=filter_files):
    """
    Takes the name of the directory and returns a
    list of files which it contains
    :param check: filter for files
    :param directory: head directory name
    :return: list of files
    """
    ret = []
    for root, _, files in os.walk(directory, topdown=False):
        ret.extend(map(lambda x: os.path.join(root, x), check(files)))
    return filter(lambda s: not os.path.islink(s), ret)
