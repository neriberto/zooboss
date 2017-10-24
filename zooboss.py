import argparse
import hashlib
import os
import Queue
import threading

END_PROCESS = False
DIR_LISTED = False
WORK = Queue.Queue()


def execute(file_path):
    if not os.path.isfile(file_path):
        return
    with open(file_path, 'rb') as fd:
        print(hashlib.md5(fd.read()).hexdigest() + ' ' + file_path)


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


def main(dir_path, destiny_path, move, n_threads):
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
            default=os.path.expanduser("~/.config/zooboss/binaries/"),
            required=False)
    parser.add_argument(
            "-m",
            "--move",
            help="Determines that the origin file must be moved",
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

    if args.origin:
        main(args.origin, args.destiny, args.move, int(args.threads))
