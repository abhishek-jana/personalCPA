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

@app.command()
def eval(
    model_path: str, 
    gold_standard: str = "eval/gold_standard.json",
    rag: bool = typer.Option(False, help="Enable RAG during evaluation.")
):
    """Evaluate a local model's performance and accuracy."""
    if not os.path.exists(model_path):
        console.print(f"[red]Error:[/red] Model not found: {model_path}")
        return

    console.print(f"[bold blue]Starting Evaluation for model:[/bold blue] {model_path} (RAG: {'ON' if rag else 'OFF'})")
    # Run the evaluation script
    cmd = f"export PYTHONPATH=$PYTHONPATH:. && uv run python eval/evaluator.py {model_path} --gold_standard {gold_standard}"
    if rag:
        cmd += " --rag"
    os.system(cmd)

@app.command()
def chat(
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Message to send to the assistant."),
    url: str = DEFAULT_URL, 
    rag: bool = typer.Option(True, help="Use RAG to ground the assistant's advice.")
):
    """Start an interactive or one-off chat session with the CPA Assistant."""
    if message:
        try:
            response = httpx.post(f"{url}/chat", json={"message": message, "use_rag": rag}, timeout=120.0)
            if response.status_code == 200:
                answer = response.json()["answer"]
                console.print(f"[bold blue]Assistant:[/bold blue] {answer}")
            else:
                console.print(f"[red]Error:[/red] {response.status_code} - {response.text}")
        except httpx.RequestError as exc:
            console.print(f"[red]An error occurred while requesting {exc.request.url!r}.[/red]")
        return

    console.print(f"[bold blue]CPA Assistant is ready (RAG: {'ON' if rag else 'OFF'}). Type 'exit' or 'quit' to end.[/bold blue]")
    while True:
        user_message = console.input("[bold green]You: [/bold green]")
        if user_message.lower() in ["exit", "quit"]:
            break
        
        try:
            response = httpx.post(f"{url}/chat", json={"message": user_message, "use_rag": rag}, timeout=120.0)
            if response.status_code == 200:
                answer = response.json()["answer"]
                console.print(f"[bold blue]Assistant:[/bold blue] {answer}")
            else:
                console.print(f"[red]Error:[/red] {response.status_code} - {response.text}")
        except httpx.RequestError as exc:
            console.print(f"[red]An error occurred while requesting {exc.request.url!r}.[/red]")

@app.command()
def add_doc(content: str, url: str = DEFAULT_URL):
    """Add a document snippet to the vector memory."""
    try:
        response = httpx.post(f"{url}/documents", json={"content": content})
        if response.status_code == 200:
            console.print(f"[green]Document saved successfully! ID: {response.json()['id']}[/green]")
        else:
            console.print(f"[red]Error:[/red] {response.status_code}")
    except httpx.RequestError as exc:
        console.print(f"[red]An error occurred while requesting {exc.request.url!r}.[/red]")

@app.command()
def search(query: str, limit: int = 3, url: str = DEFAULT_URL):
    """Search for relevant document snippets using vector search."""
    try:
        response = httpx.post(f"{url}/search", json={"query": query, "limit": limit})
        if response.status_code == 200:
            results = response.json()
            if not results:
                console.print("No relevant documents found.")
                return

            table = Table(title=f"Search Results for: '{query}'")
            table.add_column("Content", style="green")
            table.add_column("Distance", justify="right", style="cyan")

            for r in results:
                table.add_row(r["content"], f"{r['distance']:.4f}")
            console.print(table)
        else:
            console.print(f"[red]Error:[/red] {response.status_code}")
    except httpx.RequestError as exc:
        console.print(f"[red]An error occurred while requesting {exc.request.url!r}.[/red]")

if __name__ == "__main__":
    app()
