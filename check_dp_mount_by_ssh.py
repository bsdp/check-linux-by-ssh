import os
import sys
import uuid
import threading

# Ok try to load our directory to load the plugin utils.
my_dir = os.path.dirname(__file__)
sys.path.insert(0, my_dir)

try:
    import schecks
except ImportError:
    print "ERROR : this plugin needs the local schecks.py lib. Please install it"
    sys.exit(2)

VERSION = "1"
PATH = "/opt/dataprotect/storage/heartbeat"

result = threading.Event()


def check_heartbeat(res):
    """Write/read a random string into the heartbeat file."""
    client = schecks.get_client(opts)
    random_str = str(uuid.uuid4())[:8]

    write = "echo {0} > {1}".format(random_str, PATH)
    stdin, stdout, stderr = client.exec_command('export LC_LANG=C && unset LANG && %s' % write)
    if stderr:
        print "CRITICAL: Unresponsive mount!"
        sys.exit(2)

    read = "cat {0}".format(PATH)
    stdin, stdout, stderr = client.exec_command('export LC_LANG=C && unset LANG && %s' % read)
    if stderr or stdout[0] != random_str:
        print "CRITICAL: Unresponsive mount!"
        sys.exit(2)

    # Everything is OK - set the event
    res.set()

###############################################################################


parser = schecks.get_parser()

if __name__ == '__main__':
    # Ok first job : parse args
    opts, args = parser.parse_args()
    
    # Ok now got an object that link to our destination
    result = threading.Event()

    thread = threading.Thread(target=check_heartbeat, args=[result])
    thread.start()
    thread.join(timeout=2)

    if result.is_set():
        print "OK: Mount is responsive."
        sys.exit(0)
    else:
        print "CRITICAL: Unresponsive mount!"
        sys.exit(2)
