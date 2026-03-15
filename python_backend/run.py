"""
run.py
Main entry point - spawns all 5 servers via subprocess.
Windows-compatible with visible logs.
"""
import sys
import os
import subprocess
import time

# Fix Windows encoding for emojis
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def start_server(module_path, port, name):
    """Start a server in a subprocess with visible output."""
    cmd = [sys.executable, "-m", module_path]
    # Don't use PIPE - let output go directly to console
    proc = subprocess.Popen(
        cmd,
        env=os.environ.copy(),
    )
    return proc, name, port


def main():
    """Start all 5 servers."""
    print("\n" + "=" * 60)
    print("🐾 PawBook Backend - Python LangGraph + MCP")
    print("=" * 60 + "\n")

    servers = [
        ("mcp_servers.availability_server", 3101, "AVAIL"),
        ("mcp_servers.pricing_server", 3102, "PRICE"),
        ("mcp_servers.booking_server", 3103, "BOOK"),
        ("mcp_servers.notification_server", 3104, "NOTIF"),
        ("agent.agent_server", 3100, "AGENT"),
    ]

    processes = []
    print("Starting servers...\n")

    for module, port, name in servers:
        print(f"  Starting {name} on port {port}...")
        proc, name, port = start_server(module, port, name)
        processes.append((proc, name, port))
        time.sleep(1)  # Stagger startup to avoid port conflicts

    print("\n" + "=" * 60)
    print("✅ All servers started!")
    print("   Availability:  http://localhost:3101")
    print("   Pricing:       http://localhost:3102")
    print("   Booking:       http://localhost:3103")
    print("   Notification:  http://localhost:3104")
    print("   Agent:         http://localhost:3100")
    print("=" * 60)
    print("\nServer logs will appear above. Press Ctrl+C to stop.\n")

    try:
        # Keep main process alive
        while True:
            time.sleep(1)
            # Check if any process died unexpectedly
            for proc, name, port in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  {name} (port {port}) exited with code {proc.returncode}")
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        for proc, name, _ in processes:
            if proc.poll() is None:
                print(f"  Terminating {name}...")
                proc.terminate()
        time.sleep(2)
        for proc, name, _ in processes:
            if proc.poll() is None:
                print(f"  Killing {name}...")
                proc.kill()
        print("All servers stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
