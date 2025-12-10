#!/usr/bin/env python3
"""
Verify Cosmos DB container deployment and HPK configuration.

Usage:
    python scripts/verify_containers.py
    python scripts/verify_containers.py --detailed
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import argparse
from azure.cosmos import CosmosClient, exceptions
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

console = Console()


def get_cosmos_client() -> CosmosClient:
    """Get Cosmos DB client from environment."""
    connection_string = os.getenv("COSMOS_CONNECTION_STRING")
    if not connection_string:
        console.print("[red]❌ COSMOS_CONNECTION_STRING not set in environment[/red]")
        sys.exit(1)
    
    return CosmosClient.from_connection_string(connection_string)


def verify_container_exists(database, container_name: str) -> bool:
    """Check if container exists."""
    try:
        container = database.get_container_client(container_name)
        container.read()
        return True
    except exceptions.CosmosResourceNotFoundError:
        return False


def get_container_properties(database, container_name: str) -> Dict[str, Any]:
    """Get container properties including partition key info."""
    try:
        container = database.get_container_client(container_name)
        properties = container.read()
        return properties
    except exceptions.CosmosResourceNotFoundError:
        return None


def format_partition_key(partition_key: Dict) -> str:
    """Format partition key for display."""
    paths = partition_key.get("paths", [])
    kind = partition_key.get("kind", "Hash")
    
    if kind == "MultiHash":
        return f"HPK: {', '.join(paths)}"
    else:
        return f"Hash: {paths[0] if paths else 'N/A'}"


def verify_deployment(detailed: bool = False):
    """Verify Cosmos DB deployment."""
    console.print(Panel.fit(
        "[bold cyan]EVA RAG - Cosmos DB Deployment Verification[/bold cyan]",
        border_style="cyan"
    ))
    
    # Expected containers
    expected_containers = {
        "spaces": {"hpk": True, "paths": ["/space_id", "/tenant_id", "/created_by"]},
        "documents_hpk": {"hpk": True, "paths": ["/space_id", "/tenant_id", "/user_id"]},
        "chunks": {"hpk": True, "paths": ["/space_id", "/tenant_id", "/user_id"]},
        "ai_interactions": {"hpk": True, "paths": ["/space_id", "/tenant_id", "/user_id"]},
        "audit_logs": {"hpk": False, "paths": ["/sequence_number"]},
        "audit_counters": {"hpk": False, "paths": ["/id"]},
        "documents": {"hpk": False, "paths": ["/tenant_id"], "legacy": True},
    }
    
    console.print("\n[yellow]🔍 Connecting to Cosmos DB...[/yellow]")
    client = get_cosmos_client()
    database_name = os.getenv("COSMOS_DATABASE_NAME", "eva-rag")
    database = client.get_database_client(database_name)
    
    console.print(f"[green]✅ Connected to database: {database_name}[/green]\n")
    
    # Verification table
    table = Table(title="Container Verification", show_header=True, header_style="bold magenta")
    table.add_column("Container", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Partition Key", style="yellow")
    table.add_column("Type", justify="center")
    
    all_verified = True
    
    for container_name, expected in expected_containers.items():
        exists = verify_container_exists(database, container_name)
        
        if exists:
            properties = get_container_properties(database, container_name)
            partition_key = properties.get("partitionKey", {})
            pk_display = format_partition_key(partition_key)
            
            # Verify partition key configuration
            actual_paths = partition_key.get("paths", [])
            expected_paths = expected["paths"]
            pk_correct = set(actual_paths) == set(expected_paths)
            
            is_hpk = partition_key.get("kind") == "MultiHash"
            hpk_correct = is_hpk == expected["hpk"]
            
            if pk_correct and hpk_correct:
                status = "[green]✅ OK[/green]"
                container_type = "[green]HPK[/green]" if is_hpk else "Hash"
            else:
                status = "[yellow]⚠️  Mismatch[/yellow]"
                container_type = "[yellow]HPK[/yellow]" if is_hpk else "[yellow]Hash[/yellow]"
                all_verified = False
            
            if expected.get("legacy"):
                container_type = "[dim]Legacy[/dim]"
            
            table.add_row(container_name, status, pk_display, container_type)
            
            if detailed and properties:
                console.print(f"\n[dim]Container: {container_name}[/dim]")
                console.print(f"  Throughput: {properties.get('throughput', 'N/A')} RU/s")
                console.print(f"  Indexing: {properties.get('indexingPolicy', {}).get('indexingMode', 'N/A')}")
        else:
            status = "[red]❌ Missing[/red]"
            table.add_row(container_name, status, "N/A", "N/A")
            all_verified = False
    
    console.print(table)
    
    # Summary
    console.print()
    if all_verified:
        console.print(Panel.fit(
            "[bold green]✅ All containers verified successfully![/bold green]\n"
            "HPK configuration is correct.",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            "[bold yellow]⚠️  Some containers need attention[/bold yellow]\n"
            "Please review the deployment.",
            border_style="yellow"
        ))
    
    # Additional checks
    console.print("\n[yellow]📊 Additional Checks:[/yellow]")
    
    # Check database properties
    db_properties = database.read()
    console.print(f"  • Database ID: [cyan]{db_properties.get('id')}[/cyan]")
    
    # Count documents (sample)
    sample_container = "documents_hpk"
    if verify_container_exists(database, sample_container):
        container = database.get_container_client(sample_container)
        query = "SELECT VALUE COUNT(1) FROM c"
        try:
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            count = items[0] if items else 0
            console.print(f"  • Documents in '{sample_container}': [cyan]{count}[/cyan]")
        except Exception as e:
            console.print(f"  • Could not count documents: {e}")
    
    console.print()
    
    return all_verified


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Verify Cosmos DB deployment")
    parser.add_argument("--detailed", action="store_true", help="Show detailed information")
    args = parser.parse_args()
    
    try:
        success = verify_deployment(detailed=args.detailed)
        sys.exit(0 if success else 1)
    except Exception as e:
        console.print(f"[red]❌ Verification failed: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
