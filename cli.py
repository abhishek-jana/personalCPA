import typer
import httpx
from rich.console import Console
from rich.table import Table
from typing import Optional
import os

app = typer.Typer()
console = Console()

DEFAULT_URL = "http://127.0.0.1:8000"

@app.command()
def status(url: str = DEFAULT_URL):
    """Check the status of the backend server."""
    try:
        response = httpx.get(f"{url}/status")
        if response.status_code == 200:
            console.print(response.json())
        else:
            console.print(f"[red]Error:[/red] {response.status_code}")
    except httpx.RequestError as exc:
        console.print(f"[red]An error occurred while requesting {exc.request.url!r}.[/red]")

@app.command()
def add(
    date: str,
    description: str,
    amount: float,
    category: Optional[str] = typer.Option(None, "--category", "-c"),
    url: str = DEFAULT_URL
):
    """Add a new transaction manually."""
    transaction_data = {
        "date": date,
        "description": description,
        "amount": amount,
        "category": category
    }
    try:
        response = httpx.post(f"{url}/transactions", json=transaction_data)
        if response.status_code == 200:
            console.print("[green]Transaction added successfully![/green]")
            console.print(response.json())
        else:
            console.print(f"[red]Error:[/red] {response.status_code} - {response.text}")
    except httpx.RequestError as exc:
        console.print(f"[red]An error occurred while requesting {exc.request.url!r}.[/red]")

@app.command()
def list(url: str = DEFAULT_URL):
    """List all transactions."""
    try:
        response = httpx.get(f"{url}/transactions")
        if response.status_code == 200:
            transactions = response.json()
            if not transactions:
                console.print("No transactions found.")
                return

            table = Table(title="Transactions")
            table.add_column("ID", justify="right", style="cyan", no_wrap=True)
            table.add_column("Date", style="magenta")
            table.add_column("Description", style="green")
            table.add_column("Amount", justify="right", style="bold yellow")
            table.add_column("Category", style="blue")

            for t in transactions:
                table.add_row(
                    str(t["id"]),
                    t["date"],
                    t["description"],
                    f"{t['amount']:.2f}",
                    t.get("category") or ""
                )
            console.print(table)
        else:
            console.print(f"[red]Error:[/red] {response.status_code} - {response.text}")
    except httpx.RequestError as exc:
        console.print(f"[red]An error occurred while requesting {exc.request.url!r}.[/red]")

@app.command()
def import_csv(file_path: str, url: str = DEFAULT_URL):
    """Import transactions from a CSV file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        return

    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "text/csv")}
            response = httpx.post(f"{url}/import", files=files)
            
        if response.status_code == 200:
            console.print(f"[green]Successfully imported {len(response.json())} transactions![/green]")
        else:
            console.print(f"[red]Error:[/red] {response.status_code} - {response.text}")
    except httpx.RequestError as exc:
        console.print(f"[red]An error occurred while requesting {exc.request.url!r}.[/red]")

if __name__ == "__main__":
    app()
