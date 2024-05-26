from mcstatus import JavaServer
import os
import sys

MC_SERVER_ADDR_EXTERNAL = os.environ["MC_SERVER_ADDR_EXTERNAL"]


def main():
    is_up = False
    server = JavaServer.lookup(MC_SERVER_ADDR_EXTERNAL)
    try:
        status = server.status()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    else:
        is_up = True
    
    if not is_up:
        sys.exit(1)


if __name__ == '__main__':
    main()
