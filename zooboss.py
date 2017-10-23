import hashlib
import os
from Queue import Queue
import threading

END_PROCESS = False
DIR_LISTED = False
WORK = Queue()


def execute(file_path):
    with open(file_path, 'rb') as fd:
        print(hashlib.md5(fd.read()).hexdigest() + ' ' + file_path)


def worker():
    global END_PROCESS
    while not END_PROCESS:
        try:
            candidate = WORK.get(True, 5)
        except Queue.Empty:
            continue
        execute(candidate)
        WORK.task_done()


def main(dir_path):
    global END_PROCESS
    global DIR_LISTED

    threads = []
    for idx in range(8):
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        threads.append(thread)

    while not END_PROCESS:
        try:
            if not DIR_LISTED:
                for dirname, dirnames, filenames in os.walk(dir_path):
                    for filename in filenames:
                        WORK.put(os.path.join(dirname, filename))

            DIR_LISTED = True

            if WORK.qsize() == 0:
                END_PROCESS = True

        except KeyboardInterrupt:
            END_PROCESS = True
            for thread in threads:
                if thread.is_alive():
                    thread.join()


main("/home/neriberto/Documentos")
