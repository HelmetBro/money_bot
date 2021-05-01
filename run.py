import os
import sys
import infrastructure
from signal import signal, SIGABRT, SIGINT, SIGTERM

BACKTRADING = False

def main_process_cleanup(*args):
    for child in infrastructure.child_processes:
        print("terminating child process " + str(child.pid))
        os.kill(child.pid, SIGABRT)
        child.join()
    print("terminating main process " + str(os.getpid()))
    os.kill(os.getpid(), SIGABRT)

if __name__ == "__main__":
    if sys.argv[0] == '-b' or sys.argv[0] == "--backtrader":
        BACKTRADING = True
    try:
        # for sig in (SIGINT, SIGTERM):
        #     signal(sig, main_process_cleanup)
        infrastructure.main()
    except Exception as e:
        main_process_cleanup()