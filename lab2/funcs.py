import hashlib
import os
from itertools import product


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
    eqls = {}
    for file in files:
        try:
            eqls[take_hash(file, read_length)].append(file)
        except KeyError:
            eqls[take_hash(file, read_length)] = [file]
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
        ret.extend(product([root + os.path.sep], check(files)))
    return map(lambda x: x[0] + x[1], ret)
