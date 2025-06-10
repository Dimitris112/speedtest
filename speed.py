import speedtest
import datetime
import csv
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

def test_internet_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()

        console.print("[cyan]Running download and upload tests...[/cyan]")
        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000
        ping = st.results.ping
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "timestamp": timestamp,
            "download": download_speed,
            "upload": upload_speed,
            "ping": ping
        }

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

def save_to_csv(result, filename="test.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "download", "upload", "ping"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)

def display_result(result):
    table = Table(title="Internet Speed Test Result", show_lines=True)

    table.add_column("Timestamp", justify="center")
    table.add_column("Download (Mbps)", justify="right")
    table.add_column("Upload (Mbps)", justify="right")
    table.add_column("Ping (ms)", justify="right")

    table.add_row(
        result["timestamp"],
        f"{result['download']:.2f}",
        f"{result['upload']:.2f}",
        f"{result['ping']:.2f}"
    )

    console.print(table)

def run_tests(count=1, delay=5):
    for _ in track(range(count), description="Running speed tests..."):
        result = test_internet_speed()
        display_result(result)
        save_to_csv(result)
        if count > 1:
            import time
            time.sleep(delay)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Internet Speed Test CLI Tool")
    parser.add_argument("-n", "--number", type=int, default=1, help="Number of tests to run")
    parser.add_argument("-d", "--delay", type=int, default=5, help="Delay between tests")

    args = parser.parse_args()
    if args.number < 1:
        console.print("[red]Error:[/red] The number of tests must be at least 1.")
        sys.exit(1)
    run_tests(count=args.number, delay=args.delay)