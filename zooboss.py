import argparse
import hashlib
import os
import Queue
import shutil
import threading

END_PROCESS = False
DIR_LISTED = False
WORK = Queue.Queue()
DESTINY_PATH = os.path.expanduser("~/.config/zooboss/binaries/")
USE_MOVE = False
USE_MAGIC = False


def create_new_path(file_hash):
    directory = os.path.join(
            DESTINY_PATH,
            file_hash[0:2],
            file_hash[2:4],
            file_hash[4:6],
            file_hash[6:8])
    if not os.path.isdir(directory):
        os.makedirs(directory)
    return os.path.join(directory, file_hash)


def execute(file_path):
    if not os.path.isfile(file_path):
        return
    with open(file_path, 'rb') as fd:
        file_hash = hashlib.md5(fd.read()).hexdigest()
        print(file_hash + ' ' + file_path)
        new_file_path = create_new_path(file_hash)
        # if path not exists
        if not os.path.exists(new_file_path):
            if USE_MOVE:  # if must move
                shutil.move(file_path, new_file_path)
            else:  # else just copy maintaining the original file
                shutil.copy(file_path, new_file_path)
        else:  # if path already exists
            if USE_MOVE:  # and we must move
                os.remove(file_path)  # the delete original file


def worker():
    global END_PROCESS
    global WORK
    while not END_PROCESS:
        try:
            candidate = WORK.get(True, 5)
        except Queue.Empty:
            continue
        execute(candidate)
        WORK.task_done()


def threads_stop(threads):
    global END_PROCESS
    END_PROCESS = True
    for thread in threads:
        if thread.is_alive():
            thread.join()


def main(dir_path, n_threads):
    global END_PROCESS
    global DIR_LISTED

    try:
        threads = []
        for idx in range(n_threads):
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)

        while not END_PROCESS:
            if not DIR_LISTED:
                for dirname, dirnames, filenames in os.walk(dir_path):
                    for filename in filenames:
                        WORK.put(os.path.join(dirname, filename))

            DIR_LISTED = True

            if WORK.qsize() == 0:
                threads_stop(threads)

    except KeyboardInterrupt:
        threads_stop(threads)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "-o",
            "--origin",
            help='The path to be scanned',
            action='store',
            required=True)
    parser.add_argument(
            "-d",
            "--destiny",
            help="The destiny path to store files",
            action="store",
            default=DESTINY_PATH,
            required=False)
    parser.add_argument(
            "-m",
            "--move",
            help="Determines that the origin file must be moved",
            action="store_true",
            default=False,
            required=False)
    parser.add_argument(
            "-f",
            "--filetype",
            help="Determines that the destiny will use the file type",
            action="store_true",
            default=False,
            required=False)
    parser.add_argument(
            "-t",
            "--threads",
            help="The number of threads",
            action="store",
            default=2,
            required=False)

    args = parser.parse_args()

    if args.destiny:
        DESTINY_PATH = args.destiny

    if args.move:
        USE_MOVE = args.move

    if args.filetype:
        USE_MAGIC = args.filetype

    if args.origin:
        main(args.origin, int(args.threads))
