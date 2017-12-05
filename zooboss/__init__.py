import argparse
import hashlib
import logging
import os
import Queue
import shutil
import sys
import threading

END_PROCESS = False
DIR_LISTED = False
WORK = Queue.Queue()
DESTINY_PATH = os.path.expanduser("~/.zooboss/binaries/")
USE_MOVE = False
USE_MAGIC = False


def get_file_type(file_path):
    """Get file real file type."""
    try:
        import subprocess
        file_process = subprocess.Popen(
            ['file', '-b', file_path], stdout=subprocess.PIPE)
        return file_process.stdout.read().strip()
    except:
        return None


def create_new_path(file_hash, file_type):
    """Create a new file path."""
    if USE_MAGIC:
        if file_type is not None:
            mime = file_type.split()[0].lower()
        else:
            mime = "unknown"
        directory = os.path.join(DESTINY_PATH, mime)
    else:
        directory = os.path.join(DESTINY_PATH)

    directory = os.path.join(
        directory,
        file_hash[0],
        file_hash[1],
        file_hash[2],
        file_hash[3])
    if not os.path.isdir(directory):
        os.makedirs(directory)
    return os.path.join(directory, file_hash)


def execute(file_path):
    """Execute the file analysis."""
    if not os.path.isfile(file_path):
        return
    with open(file_path, 'rb') as file_descriptor:
        if USE_MAGIC:
            file_type = get_file_type(file_path)
        else:
            file_type = None
        file_hash = hashlib.sha256(file_descriptor.read()).hexdigest()
        logging.info(file_hash + ' ' + file_path)
        new_file_path = create_new_path(file_hash, file_type)
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
    """The function worker that runs in a thread."""
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
    """Stop the threads."""
    global END_PROCESS
    END_PROCESS = True
    for thread in threads:
        if thread.is_alive():
            thread.join()


def main():
    """Start the threads."""
    global END_PROCESS
    global DIR_LISTED
    global DESTINY_PATH
    global USE_MOVE
    global USE_MAGIC

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%y-%m-%d %H:%M:%S',
        stream=sys.stdout)
    logging.getLogger("zooboss")
    logging.addLevelName(
        logging.WARNING,
        '\033[1;31m%s\033[1;0m' % logging.getLevelName(logging.WARNING))

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

    if not args.origin:
        return

    try:
        threads = []
        for idx in range(int(args.threads)):
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)

        while not END_PROCESS:
            if not DIR_LISTED:
                for dirname, dirnames, filenames in os.walk(args.origin):
                    for filename in filenames:
                        WORK.put(os.path.join(dirname, filename))

            DIR_LISTED = True

            if WORK.qsize() == 0:
                threads_stop(threads)

    except KeyboardInterrupt:
        threads_stop(threads)


if __name__ == '__main__':
    sys.exit(main())
