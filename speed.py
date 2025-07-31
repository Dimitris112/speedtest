import speedtest
import datetime
import csv
import os
import sys
import time
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# speedtest instance for connection reuse
st_instance = None

def get_speedtest_instance():
    """Get or create speedtest instance for reuse across multiple tests"""
    global st_instance
    if st_instance is None:
        console.print("[yellow]Initializing connection...[/yellow]")
        st_instance = speedtest.Speedtest()
        st_instance.get_best_server()
        server = st_instance.results.server
        console.print(f"[green]Connected to: {server['sponsor']} ({server['name']})[/green]")
    return st_instance

def test_internet_speed():
    try:
        st = get_speedtest_instance()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            # Download
            progress.add_task("Testing download speed...", total=None)
            download_speed = st.download() / 1_000_000
            
            # Upload
            progress.add_task("Testing upload speed...", total=None)
            upload_speed = st.upload() / 1_000_000

        ping = st.results.ping
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "timestamp": timestamp,
            "download": round(download_speed, 2),
            "upload": round(upload_speed, 2),
            "ping": round(ping, 2)
        }

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return None

def save_to_csv(result, filename="test.csv"):
    if not result:
        return
        
    file_exists = os.path.isfile(filename)
    try:
        with open(filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["timestamp", "download", "upload", "ping"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(result)
    except Exception as e:
        console.print(f"[red]Error saving to CSV file:[/red] {e}")

def display_result(result):
    if not result:
        return
        
    table = Table(title="Internet Speed Test Result", show_lines=True)
    table.add_column("Timestamp", justify="center", style="cyan")
    table.add_column("Download (Mbps)", justify="right", style="green")
    table.add_column("Upload (Mbps)", justify="right", style="blue")
    table.add_column("Ping (ms)", justify="right", style="yellow")

    table.add_row(
        result["timestamp"],
        f"{result['download']:.2f}",
        f"{result['upload']:.2f}",
        f"{result['ping']:.2f}"
    )
    console.print(table)

def display_summary(results):
    if len(results) <= 1:
        return
        
    downloads = [r['download'] for r in results]
    uploads = [r['upload'] for r in results]
    pings = [r['ping'] for r in results]
    
    summary_table = Table(title="Test Summary", show_lines=True)
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Average", justify="right")
    summary_table.add_column("Min", justify="right")
    summary_table.add_column("Max", justify="right")
    
    summary_table.add_row(
        "Download (Mbps)",
        f"{sum(downloads)/len(downloads):.2f}",
        f"{min(downloads):.2f}",
        f"{max(downloads):.2f}"
    )
    summary_table.add_row(
        "Upload (Mbps)",
        f"{sum(uploads)/len(uploads):.2f}",
        f"{min(uploads):.2f}",
        f"{max(uploads):.2f}"
    )
    summary_table.add_row(
        "Ping (ms)",
        f"{sum(pings)/len(pings):.2f}",
        f"{min(pings):.2f}",
        f"{max(pings):.2f}"
    )
    
    console.print(summary_table)

def run_tests(count=1, delay=5): # Default 1 test - delay 5 sec between tests
    results = []
    failed_tests = 0
    
    console.print(f"[bold blue]Starting {count} speed test{'s' if count > 1 else ''}...[/bold blue]")
    
    for i in range(count):
        if count > 1:
            console.print(f"\n[bold]Test {i+1}/{count}[/bold]")
            
        result = test_internet_speed()
        if result:
            display_result(result)
            save_to_csv(result)
            results.append(result)
        else:
            failed_tests += 1
            
        # Delay between tests - only if more than one test
        if i < count - 1 and count > 1:
            console.print(f"[dim]Waiting {delay} seconds...[/dim]")
            time.sleep(delay)
    
    # Show final results
    if count > 1:
        console.print(f"\n[green]Completed: {len(results)} successful tests[/green]")
        if failed_tests > 0:
            console.print(f"[red]Failed: {failed_tests} tests[/red]")
        display_summary(results)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Internet Speed Test")
    parser.add_argument("-n", "--number", type=int, default=1, help="Number of tests to run")
    parser.add_argument("-d", "--delay", type=int, default=5, help="Delay between tests")

    args = parser.parse_args()
    if args.number < 1:
        console.print("[red]Error:[/red] The number of tests must be at least 1.")
        sys.exit(1)
        
    try:
        run_tests(count=args.number, delay=args.delay)
    except KeyboardInterrupt:
        console.print("\n[yellow]Tests interrupted.[/yellow]")
        sys.exit(0)