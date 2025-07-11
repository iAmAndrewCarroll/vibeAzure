"""
Azure Cost CLI Tracker with enhanced error handling and AI insights
"""
import subprocess
import json
import webbrowser
import sys
from typing import List, Tuple, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich import print
from rich.panel import Panel

from llm_handler import LLMHandler
from azure_parser import AzureResourceParser

console = Console()

class AzureCostTracker:
    def __init__(self):
        self.costs: List[Tuple[float, str]] = []
        self.llm_handler: Optional[LLMHandler] = None
        self.parser = AzureResourceParser()
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM handler with fallback options"""
        try:
            # Try Ollama first (easier setup)
            self.llm_handler = LLMHandler(backend="ollama", model_name="tinyllama")
            console.print("[green]✓ Ollama LLM initialized[/green]")
        except Exception:
            try:
                # Fallback to llama-cpp-python
                self.llm_handler = LLMHandler(backend="llama-cpp", model_name="tinyllama")
                console.print("[green]✓ Llama-cpp LLM initialized[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ LLM initialization failed: {e}[/yellow]")
                console.print("[yellow]AI features will be disabled[/yellow]")
    
    def get_costs(self) -> bool:
        """Fetch Azure costs using Azure CLI"""
        console.print("[blue]Fetching Azure costs...[/blue]")
        
        try:
            # First, verify Azure CLI is logged in
            login_check = subprocess.run(
                ["az", "account", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if login_check.returncode != 0:
                console.print("[red]❌ Not logged into Azure CLI. Run: az login[/red]")
                return False
            
            # Build cost management query
            dataset = {
                "granularity": "None",
                "aggregation": {
                    "totalCost": {"name": "PreTaxCost", "function": "Sum"}
                },
                "grouping": [{"type": "Dimension", "name": "ResourceId"}]
            }
            
            cmd = [
                "az", "costmanagement", "query",
                "--type", "ActualCost",
                "--timeframe", "MonthToDate",
                "--dataset", json.dumps(dataset)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                console.print(f"[red]❌ Failed to fetch costs: {result.stderr}[/red]")
                return False
            
            # Parse results
            try:
                data = json.loads(result.stdout)
                rows = data.get("properties", {}).get("rows", [])
                
                if not rows:
                    console.print("[yellow]No cost data found for this month[/yellow]")
                    return False
                
                # Convert to (cost, resource_id) tuples and sort by cost
                self.costs = []
                for row in rows:
                    if len(row) >= 2:
                        cost = float(row[0]) if row[0] else 0.0
                        resource_id = str(row[1]) if row[1] else "Unknown"
                        if cost > 0:  # Only include resources with actual cost
                            self.costs.append((cost, resource_id))
                
                self.costs.sort(reverse=True)  # Sort by cost descending
                
                console.print(f"[green]✓ Found {len(self.costs)} resources with costs[/green]")
                return True
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                console.print(f"[red]❌ Failed to parse cost data: {e}[/red]")
                return False
        
        except subprocess.TimeoutExpired:
            console.print("[red]❌ Azure CLI request timed out[/red]")
            return False
        except FileNotFoundError:
            console.print("[red]❌ Azure CLI not found. Using demo mode with sample data.[/red]")
            return self._load_demo_data()
        except Exception as e:
            console.print(f"[red]❌ Unexpected error: {e}[/red]")
            # Try demo mode as fallback
            console.print("[yellow]Trying demo mode as fallback...[/yellow]")
            return self._load_demo_data()
    
    def _load_demo_data(self) -> bool:
        """Load demo data when Azure CLI is not available"""
        console.print("[yellow]📊 Loading demo data for testing...[/yellow]")
        
        # Sample Azure resource costs for demonstration
        demo_costs = [
            (125.50, "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-webapp/providers/Microsoft.Web/sites/mywebapp"),
            (89.20, "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-storage/providers/Microsoft.Storage/storageAccounts/mystorageaccount"),
            (45.75, "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-vm/providers/Microsoft.Compute/virtualMachines/myvm"),
            (32.10, "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-db/providers/Microsoft.Sql/servers/mysqlserver"),
            (18.90, "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-network/providers/Microsoft.Network/publicIPAddresses/mypublicip"),
            (12.45, "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-keyvault/providers/Microsoft.KeyVault/vaults/mykeyvault"),
            (8.75, "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-cognitive/providers/Microsoft.CognitiveServices/accounts/mycognitive"),
            (6.20, "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-container/providers/Microsoft.ContainerService/managedClusters/myaks"),
        ]
        
        self.costs = demo_costs
        console.print(f"[green]✓ Loaded {len(self.costs)} demo resources[/green]")
        console.print("[yellow]💡 This is demo data. Install Azure CLI and log in for real data.[/yellow]")
        return True
    
    def print_menu(self):
        """Display the main menu"""
        console.print()
        console.print(Panel.fit(
            "[bold cyan]Azure Cost CLI Tracker[/bold cyan]",
            border_style="blue"
        ))
        console.print("1. 📊 Show resources incurring costs")
        console.print("2. 🌐 Open resource in Azure Portal")
        console.print("3. 🤖 Ask AI for cost analysis")
        console.print("4. 📈 Show cost summary by category")
        console.print("5. 🔄 Refresh cost data")
        console.print("6. ❌ Exit")
    
    def show_costs(self):
        """Display costs in a formatted table"""
        if not self.costs:
            console.print("[yellow]No cost data available. Try option 5 to refresh.[/yellow]")
            return
        
        table = Table(title="Azure Resources by Cost (Month to Date)")
        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("Cost (USD)", style="green", justify="right")
        table.add_column("Resource Name", style="white")
        table.add_column("Type", style="blue")
        table.add_column("Category", style="magenta")
        
        for i, (cost, resource_id) in enumerate(self.costs[:20], 1):
            display_name = self.parser.get_resource_display_name(resource_id)
            parsed = self.parser.parse_resource_id(resource_id)
            resource_type = parsed['resource_type'] if parsed else "Unknown"
            category = self.parser.get_cost_category(resource_id)
            
            table.add_row(
                str(i),
                f"${cost:.2f}",
                display_name,
                resource_type,
                category
            )
        
        console.print(table)
        
        if len(self.costs) > 20:
            console.print(f"[dim]... and {len(self.costs) - 20} more resources[/dim]")
    
    def open_in_portal(self):
        """Open a resource in Azure Portal"""
        if not self.costs:
            console.print("[yellow]No cost data available[/yellow]")
            return
        
        self.show_costs()
        
        try:
            choice = IntPrompt.ask(
                "Enter resource number to open in portal",
                default=1,
                show_default=True
            )
            
            if choice < 1 or choice > len(self.costs):
                console.print("[red]Invalid selection[/red]")
                return
            
            _, resource_id = self.costs[choice - 1]
            url = self.parser.make_portal_url(resource_id)
            
            if url:
                console.print(f"[blue]🌐 Opening in browser:[/blue] {url}")
                webbrowser.open(url)
            else:
                console.print("[red]❌ Could not generate portal URL[/red]")
                
        except (ValueError, KeyboardInterrupt):
            console.print("[yellow]Operation cancelled[/yellow]")
    
    def ask_ai(self):
        """Get AI analysis of costs"""
        if not self.llm_handler:
            console.print("[red]❌ AI features not available[/red]")
            return
        
        if not self.costs:
            console.print("[yellow]No cost data available[/yellow]")
            return
        
        console.print("[blue]🤖 Analyzing costs with AI...[/blue]")
        
        # Prepare cost summary for AI
        top_costs = self.costs[:10]
        total_cost = sum(cost for cost, _ in self.costs)
        
        summary_lines = []
        for cost, resource_id in top_costs:
            display_name = self.parser.get_resource_display_name(resource_id)
            category = self.parser.get_cost_category(resource_id)
            percentage = (cost / total_cost) * 100 if total_cost > 0 else 0
            summary_lines.append(f"${cost:.2f} ({percentage:.1f}%) - {display_name} [{category}]")
        
        summary = "\n".join(summary_lines)
        
        prompt = f"""You are an Azure cloud cost optimization expert. 
Analyze these resources and their costs for the current month:

Total Monthly Cost: ${total_cost:.2f}
Top Resources:
{summary}

Provide specific recommendations for:
1. Which resources are unusually expensive
2. Potential cost savings opportunities
3. Resources that might be candidates for shutdown or resizing

Be concise and actionable."""
        
        try:
            response = self.llm_handler.ask(prompt)
            console.print(Panel(
                response,
                title="🤖 AI Cost Analysis",
                border_style="green"
            ))
        except Exception as e:
            console.print(f"[red]❌ AI analysis failed: {e}[/red]")
    
    def show_category_summary(self):
        """Show cost summary by category"""
        if not self.costs:
            console.print("[yellow]No cost data available[/yellow]")
            return
        
        # Group by category
        categories = {}
        for cost, resource_id in self.costs:
            category = self.parser.get_cost_category(resource_id)
            if category not in categories:
                categories[category] = []
            categories[category].append(cost)
        
        # Create summary table
        table = Table(title="Cost Summary by Category")
        table.add_column("Category", style="cyan")
        table.add_column("Total Cost", style="green", justify="right")
        table.add_column("Resources", style="white", justify="center")
        table.add_column("Avg Cost", style="yellow", justify="right")
        
        total_cost = sum(cost for cost, _ in self.costs)
        
        for category, costs in sorted(categories.items(), key=lambda x: sum(x[1]), reverse=True):
            category_total = sum(costs)
            resource_count = len(costs)
            avg_cost = category_total / resource_count if resource_count > 0 else 0
            percentage = (category_total / total_cost) * 100 if total_cost > 0 else 0
            
            table.add_row(
                category,
                f"${category_total:.2f} ({percentage:.1f}%)",
                str(resource_count),
                f"${avg_cost:.2f}"
            )
        
        console.print(table)
    
    def run(self):
        """Main application loop"""
        console.print("[bold green]Azure Cost CLI Tracker[/bold green]")
        console.print("Loading initial cost data...")
        
        if not self.get_costs():
            console.print("[red]❌ Failed to load cost data. Exiting.[/red]")
            return
        
        while True:
            try:
                self.print_menu()
                choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6"])
                
                if choice == "1":
                    self.show_costs()
                elif choice == "2":
                    self.open_in_portal()
                elif choice == "3":
                    self.ask_ai()
                elif choice == "4":
                    self.show_category_summary()
                elif choice == "5":
                    self.get_costs()
                elif choice == "6":
                    console.print("[green]👋 Goodbye![/green]")
                    break
                
                # Pause for user to read output
                if choice != "6":
                    Prompt.ask("\nPress Enter to continue", default="")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Operation cancelled by user[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]❌ Unexpected error: {e}[/red]")

def main():
    """Entry point"""
    try:
        tracker = AzureCostTracker()
        tracker.run()
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
