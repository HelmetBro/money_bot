import os
import argparse
import infrastructure
from signal import signal, SIGABRT, SIGINT, SIGTERM

# parsing arguments and setting global BACKTRADING var
# Must be accessed by from run import BACKTRADING as BACKTRADING
parser = argparse.ArgumentParser()
parser.add_argument("-b", "--backtrader",
                    help="runs algorithm with backtrading data",
                    action="store_true")
BACKTRADING = parser.parse_args().backtrader

def main_process_cleanup(*args):
    for child in infrastructure.child_processes:
        print("terminating child process " + str(child.pid))
        os.kill(child.pid, SIGABRT)
        child.join()
    print("terminating main process " + str(os.getpid()))
    os.kill(os.getpid(), SIGABRT)

if __name__ == "__main__":
    try:
        # for sig in (SIGINT, SIGTERM):
        #     signal(sig, main_process_cleanup)
        infrastructure.main()
    except Exception as e:
        main_process_cleanup()