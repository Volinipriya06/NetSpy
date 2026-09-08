# NetSpy: Local Network & Port Discovery Utility

NetSpy is a dependency-free Python 3 command-line utility that identifies the host's outbound local IPv4 address and concurrently checks a curated list of high-value TCP ports on a chosen host. It is intended for authorized local troubleshooting, lab exercises, and portfolio demonstration of low-level socket programming.

> **Authorization required:** Scan only systems you own or have explicit permission to assess. A port scan can trigger monitoring alerts and may violate policy or law without authorization.

## Live demo output

[![NetSpy GitHub Pages deployment](https://github.com/Volinipriya06/NetSpy/actions/workflows/deploy-pages.yml/badge.svg)](https://volinipriya06.github.io/NetSpy/)
[![Run NetSpy demo](https://github.com/Volinipriya06/NetSpy/actions/workflows/demo-output.yml/badge.svg)](https://github.com/Volinipriya06/NetSpy/actions/workflows/demo-output.yml)

- **Live portfolio demo:** [volinipriya06.github.io/NetSpy](https://volinipriya06.github.io/NetSpy/)
- **Reproducible command-line output:** [GitHub Actions demo run](https://github.com/Volinipriya06/NetSpy/actions/workflows/demo-output.yml)

The live page is an interactive presentation of captured authorized loopback output. The command-line tool performs real network scans only when run locally. The workflow runs NetSpy against the runner's authorized loopback target (`127.0.0.1`); open a completed run and download the **netspy-demo-output** artifact to view the captured terminal output.

## Overview

The default target is the detected local IPv4 address. Pass a hostname or IPv4 address to scan an explicitly selected target. NetSpy checks TCP ports `21`, `22`, `23`, `25`, `80`, `135`, `443`, `445`, and `3389`, including common FTP, SSH, Telnet, SMTP, web, Windows RPC/SMB, and RDP services.

Every connection uses a one-second timeout and `socket.connect_ex`. A return value of `0` is recorded as open. Each worker owns and closes its socket, even if an exception occurs.

## Architecture

```text
                 ┌─────────────────────┐
                 │ CLI: target optional │
                 └──────────┬──────────┘
                            │
              ┌─────────────▼──────────────┐
              │ UDP route probe (no packet) │
              │ local IPv4 + /24 estimate   │
              └─────────────┬──────────────┘
                            │
                 ┌──────────▼──────────┐
                 │ hostname resolution │
                 └──────────┬──────────┘
                            │
       ┌────────────────────▼───────────────────┐
       │ Thread-per-port TCP socket workers      │
       │ settimeout(1.0) → connect_ex → close()  │
       └────────────────────┬───────────────────┘
                            │
                 ┌──────────▼──────────┐
                 │ Locked result list  │
                 │ + execution summary │
                 └─────────────────────┘
```

The displayed network boundary is a clearly labelled `/24` estimate. The Python socket API does not expose the active interface's netmask portably without platform-specific commands or additional libraries.

## Requirements

- Python 3.9 or newer for native execution
- Docker (optional)
- Network authorization for the chosen target

NetSpy has **zero third-party dependencies**.

## Installation and usage

Clone or copy the project, then run it natively:

```bash
python netspy.py
python netspy.py 127.0.0.1
python netspy.py server.lab.example
```

Use `--help` for the CLI reminder:

```bash
python netspy.py --help
```

Build and run the Docker image:

```bash
docker build -t netspy .
docker run --rm -it netspy
docker run --rm -it netspy 127.0.0.1
```

Docker network namespaces are isolated by default; the container's `127.0.0.1` is the container, not the host. Use an authorized, reachable IP address or an appropriate Docker network configuration for your environment.

## Example output

```text
[+] Local IP:          192.168.1.20
[+] Network boundary:  192.168.1.0/24 (estimated)
[+] Scan target:       127.0.0.1 (127.0.0.1)
[OPEN] 127.0.0.1:443

==========================================================
                     SCAN SUMMARY
==========================================================
Target:              127.0.0.1
Total ports scanned: 9
Execution time:      0.014 seconds
Open endpoints:
  - 127.0.0.1:443 (TCP/443)
==========================================================
```

## Wireshark verification guide

1. Obtain permission and start Wireshark on the interface carrying traffic to the authorized target. To inspect loopback traffic, select the loopback capture interface supported by your operating system.
2. Start capture, run NetSpy against the target, then stop capture.
3. Apply the display filter `tcp.flags.syn == 1` to find connection attempts. Each worker begins with a TCP **SYN**.
4. For an open TCP port, follow the stream or use `tcp.port == 443` (replace as needed). The target replies **SYN, ACK**; NetSpy completes the handshake with **ACK**, then closes the successful connection.
5. For a closed reachable port, filter with `tcp.flags.reset == 1`. The target commonly responds to the SYN with **RST, ACK**. A filtered port may yield no reply and complete only after NetSpy's one-second timeout.

This packet-level view demonstrates the mapping between `connect_ex` results and TCP state: successful handshakes produce a zero result, resets indicate refusal, and silence generally surfaces as a timeout.

## Project files

```text
.
├── netspy.py    # Application and socket scanning logic
├── Dockerfile   # Minimal Python 3.9 container image
└── README.md    # Usage, architecture, and Wireshark workflow
```
