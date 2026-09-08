const output = `$ python netspy.py 127.0.0.1

 _   _      _   ____
| \\ | | ___| |_/ ___| _ __  _   _
|  \\| |/ _ \\ __\\___ \\| '_ \\| | | |
| |\\  |  __/ |_ ___) | |_) | |_| |
|_| \\_|\\___|\\__|____/| .__/ \\__, |
                     |_|    |___/
        Local Network & Port Discovery Utility

[+] Local IP:          127.0.0.1
[+] Network boundary:  127.0.0.0/24 (estimated)
[+] Scan target:       127.0.0.1 (127.0.0.1)
[+] Timeout/port:      1.0s
[+] Starting 9 concurrent TCP checks...

==========================================================
                     SCAN SUMMARY
==========================================================
Target:              127.0.0.1
Total ports scanned: 9
Execution time:      0.003 seconds
Open endpoints:
  - None detected
==========================================================`;

const terminal = document.getElementById("terminal-output");
const runButton = document.getElementById("run-demo");

runButton.addEventListener("click", () => {
  terminal.textContent = "$ python netspy.py 127.0.0.1\n\nRunning authorized loopback scan...";
  runButton.disabled = true;
  runButton.textContent = "Replaying output…";
  window.setTimeout(() => {
    terminal.textContent = output;
    runButton.disabled = false;
    runButton.innerHTML = "Replay demo output <span aria-hidden=\"true\">→</span>";
  }, 650);
});

document.getElementById("copy-command").addEventListener("click", async (event) => {
  try {
    await navigator.clipboard.writeText("python netspy.py 127.0.0.1");
    event.currentTarget.textContent = "Copied";
    window.setTimeout(() => { event.currentTarget.textContent = "Copy"; }, 1200);
  } catch (_) {
    event.currentTarget.textContent = "Copy manually";
  }
});
