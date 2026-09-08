#!/usr/bin/env python3
"""NetSpy: a dependency-free local endpoint and TCP port discovery utility.

Only scan hosts and networks that you own or are explicitly authorized to test.
"""

import socket
import sys
import threading
from datetime import datetime


PORTS = (21, 22, 23, 25, 80, 135, 443, 445, 3389)
SOCKET_TIMEOUT = 1.0


def print_banner():
    """Print a compact, readable application banner."""
    print(r"""
 _   _      _   ____              
| \ | | ___| |_/ ___| _ __  _   _ 
|  \| |/ _ \ __\___ \| '_ \| | | |
| |\  |  __/ |_ ___) | |_) | |_| |
|_| \_|\___|\__|____/| .__/ \__, |
                     |_|    |___/ 
        Local Network & Port Discovery Utility
""")


def get_local_ip():
    """Discover the outbound local IPv4 address without sending any traffic.

    UDP ``connect`` only asks the operating system to select a route; it does
    not transmit a packet. A loopback address is used as a safe fallback when
    no active route is available (for example, in an offline container).
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No packet is sent by this call. The address merely selects a route.
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except (socket.gaierror, socket.error, OSError) as error:
        print("[!] Local IP discovery failed: {0}".format(error))
        return "127.0.0.1"
    finally:
        if sock is not None:
            sock.close()


def get_network_boundary(ip_address):
    """Return a readable conventional /24 IPv4 LAN boundary for display.

    Socket-only Python does not expose interface netmasks portably. /24 is a
    common LAN convention, so this is an *estimated* boundary, not an
    authoritative routing-table result.
    """
    try:
        octets = ip_address.split(".")
        if len(octets) == 4 and all(0 <= int(octet) <= 255 for octet in octets):
            return "{0}.{1}.{2}.0/24 (estimated)".format(*octets[:3])
    except ValueError:
        pass
    return "unavailable"


def resolve_target(target):
    """Resolve a user-provided hostname or IPv4 address to an IPv4 endpoint."""
    try:
        return socket.gethostbyname(target)
    except socket.gaierror as error:
        print("[!] Could not resolve target '{0}': {1}".format(target, error))
        return None
    except (socket.error, OSError) as error:
        print("[!] Target resolution error: {0}".format(error))
        return None


def scan_port(target_ip, port, open_endpoints, results_lock):
    """Test one TCP port and add successful connections under a mutex.

    ``connect_ex`` returns zero only when the TCP connection succeeds. Closing
    the socket in ``finally`` ensures every attempt releases its descriptor.
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(SOCKET_TIMEOUT)
        if sock.connect_ex((target_ip, port)) == 0:
            with results_lock:
                open_endpoints.append((port, "{0}:{1}".format(target_ip, port)))
            print("[OPEN] {0}:{1}".format(target_ip, port))
    except socket.gaierror as error:
        print("[!] Address error on port {0}: {1}".format(port, error))
    except (socket.timeout, socket.error, OSError) as error:
        # Closed, filtered, or unreachable ports are normal scan outcomes.
        print("[INFO] Port {0}: {1}".format(port, error))
    finally:
        if sock is not None:
            sock.close()


def scan_ports(target_ip, ports):
    """Scan ports concurrently using one bounded native thread per port."""
    open_endpoints = []
    results_lock = threading.Lock()
    threads = []

    for port in ports:
        worker = threading.Thread(
            target=scan_port,
            args=(target_ip, port, open_endpoints, results_lock),
            name="netspy-{0}".format(port),
        )
        worker.start()
        threads.append(worker)

    for worker in threads:
        worker.join()

    return sorted(open_endpoints)


def print_usage():
    print("Usage: python netspy.py [target-hostname-or-ip]")
    print("Without a target, NetSpy scans the detected local IPv4 address.")


def main():
    """Run discovery, concurrent scanning, and a deterministic final summary."""
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help")):
        print_usage()
        return 0

    print_banner()
    local_ip = get_local_ip()
    target_input = sys.argv[1] if len(sys.argv) == 2 else local_ip
    target_ip = resolve_target(target_input)
    if target_ip is None:
        return 1

    print("[+] Local IP:          {0}".format(local_ip))
    print("[+] Network boundary:  {0}".format(get_network_boundary(local_ip)))
    print("[+] Scan target:       {0} ({1})".format(target_input, target_ip))
    print("[+] Timeout/port:      {0:.1f}s".format(SOCKET_TIMEOUT))
    print("[+] Starting {0} concurrent TCP checks...\n".format(len(PORTS)))

    started_at = datetime.now()
    open_endpoints = scan_ports(target_ip, PORTS)
    elapsed = (datetime.now() - started_at).total_seconds()

    print("\n" + "=" * 58)
    print("                     SCAN SUMMARY")
    print("=" * 58)
    print("Target:              {0}".format(target_ip))
    print("Total ports scanned: {0}".format(len(PORTS)))
    print("Execution time:      {0:.3f} seconds".format(elapsed))
    print("Open endpoints:")
    if open_endpoints:
        for port, endpoint in open_endpoints:
            print("  - {0} (TCP/{1})".format(endpoint, port))
    else:
        print("  - None detected")
    print("=" * 58)
    return 0


if __name__ == "__main__":
    sys.exit(main())
