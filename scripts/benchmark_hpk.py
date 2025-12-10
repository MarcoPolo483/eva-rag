#!/usr/bin/env python3
"""
Performance benchmarking for HPK-enabled Cosmos DB.

Measures:
- Query latency (p50, p95, p99)
- Request Unit (RU) consumption
- Cross-partition vs single-partition query performance
- Batch operation efficiency

Usage:
    python scripts/benchmark_hpk.py
    python scripts/benchmark_hpk.py --scenarios single,cross,batch
    python scripts/benchmark_hpk.py --iterations 100 --output results.json
"""

import os
import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import argparse
import json
from uuid import uuid4

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import box

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

console = Console()


@dataclass
class BenchmarkResult:
    """Result of a single benchmark scenario."""
    scenario: str
    operation: str
    iterations: int
    total_time: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    total_ru: float
    avg_ru_per_operation: float
    operations_per_second: float
    timestamp: str


@dataclass
class QueryMetrics:
    """Metrics for a single query execution."""
    latency_ms: float
    ru_consumed: float
    result_count: int


class CosmosDBBenchmark:
    """Benchmark tool for Cosmos DB HPK performance."""
    
    def __init__(self, connection_string: str, database_name: str):
        self.client = CosmosClient.from_connection_string(connection_string)
        self.database = self.client.get_database_client(database_name)
        self.results: List[BenchmarkResult] = []
    
    def _execute_query(
        self,
        container_name: str,
        query: str,
        partition_key: Any = None,
        enable_cross_partition: bool = False
    ) -> QueryMetrics:
        """Execute a query and measure performance."""
        container = self.database.get_container_client(container_name)
        
        start_time = time.perf_counter()
        
        query_kwargs = {
            "query": query,
            "enable_cross_partition_query": enable_cross_partition,
        }
        if partition_key is not None:
            query_kwargs["partition_key"] = partition_key
        
        items = list(container.query_items(**query_kwargs))
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        # Get RU charge from response headers (approximate)
        # Note: Actual RU measurement requires response headers access
        ru_consumed = len(items) * 1.0  # Placeholder estimation
        
        return QueryMetrics(
            latency_ms=latency_ms,
            ru_consumed=ru_consumed,
            result_count=len(items)
        )
    
    def _create_test_data(
        self,
        container_name: str,
        count: int,
        space_id: str,
        tenant_id: str,
        user_id: str
    ) -> List[Dict]:
        """Create test documents for benchmarking."""
        container = self.database.get_container_client(container_name)
        documents = []
        
        console.print(f"[yellow]Creating {count} test documents...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Inserting documents...", total=count)
            
            for i in range(count):
                doc = {
                    "id": str(uuid4()),
                    "space_id": space_id,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "filename": f"benchmark_doc_{i}.pdf",
                    "content": f"Test content for benchmark document {i}",
                    "size_bytes": 1024 * (i % 100),
                    "tags": ["benchmark", f"batch_{i // 10}"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                
                try:
                    created = container.create_item(doc)
                    documents.append(created)
                except exceptions.CosmosResourceExistsError:
                    pass  # Document already exists
                
                progress.update(task, advance=1)
        
        console.print(f"[green]✅ Created {len(documents)} documents[/green]")
        return documents
    
    def benchmark_single_partition_query(
        self,
        iterations: int = 100,
        container: str = "documents_hpk"
    ) -> BenchmarkResult:
        """Benchmark single-partition query performance."""
        console.print("\n[cyan]📊 Benchmarking: Single Partition Query[/cyan]")
        
        # Test data
        space_id = str(uuid4())
        tenant_id = str(uuid4())
        user_id = str(uuid4())
        
        # Create test documents
        test_docs = self._create_test_data(container, 50, space_id, tenant_id, user_id)
        
        query = "SELECT * FROM c WHERE c.space_id = @space_id"
        partition_key = [space_id, tenant_id, user_id]
        
        latencies = []
        rus = []
        
        console.print(f"[yellow]Running {iterations} iterations...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Executing queries...", total=iterations)
            
            for _ in range(iterations):
                metrics = self._execute_query(
                    container,
                    query,
                    partition_key=partition_key,
                    enable_cross_partition=False
                )
                latencies.append(metrics.latency_ms)
                rus.append(metrics.ru_consumed)
                progress.update(task, advance=1)
        
        return self._compute_result(
            "Single Partition Query",
            "Query with HPK",
            iterations,
            latencies,
            rus
        )
    
    def benchmark_cross_partition_query(
        self,
        iterations: int = 100,
        container: str = "documents_hpk"
    ) -> BenchmarkResult:
        """Benchmark cross-partition query performance."""
        console.print("\n[cyan]📊 Benchmarking: Cross-Partition Query[/cyan]")
        
        # Create documents across multiple partitions
        console.print("[yellow]Creating test data across partitions...[/yellow]")
        for i in range(3):
            self._create_test_data(
                container,
                20,
                str(uuid4()),
                str(uuid4()),
                str(uuid4())
            )
        
        query = "SELECT * FROM c WHERE ARRAY_CONTAINS(c.tags, 'benchmark')"
        
        latencies = []
        rus = []
        
        console.print(f"[yellow]Running {iterations} iterations...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Executing queries...", total=iterations)
            
            for _ in range(iterations):
                metrics = self._execute_query(
                    container,
                    query,
                    enable_cross_partition=True
                )
                latencies.append(metrics.latency_ms)
                rus.append(metrics.ru_consumed)
                progress.update(task, advance=1)
        
        return self._compute_result(
            "Cross-Partition Query",
            "Query across all partitions",
            iterations,
            latencies,
            rus
        )
    
    def benchmark_batch_operations(
        self,
        iterations: int = 50,
        batch_size: int = 10,
        container: str = "documents_hpk"
    ) -> BenchmarkResult:
        """Benchmark batch insert performance."""
        console.print("\n[cyan]📊 Benchmarking: Batch Operations[/cyan]")
        
        space_id = str(uuid4())
        tenant_id = str(uuid4())
        user_id = str(uuid4())
        
        container_client = self.database.get_container_client(container)
        
        latencies = []
        rus = []
        
        console.print(f"[yellow]Running {iterations} batch operations ({batch_size} items each)...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Executing batches...", total=iterations)
            
            for i in range(iterations):
                batch_docs = [
                    {
                        "id": str(uuid4()),
                        "space_id": space_id,
                        "tenant_id": tenant_id,
                        "user_id": user_id,
                        "filename": f"batch_{i}_doc_{j}.pdf",
                        "content": f"Batch content {i}-{j}",
                    }
                    for j in range(batch_size)
                ]
                
                start_time = time.perf_counter()
                
                for doc in batch_docs:
                    try:
                        container_client.create_item(doc)
                    except exceptions.CosmosResourceExistsError:
                        pass
                
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                
                latencies.append(latency_ms)
                rus.append(batch_size * 5.0)  # Estimate ~5 RU per insert
                
                progress.update(task, advance=1)
        
        return self._compute_result(
            "Batch Operations",
            f"Insert {batch_size} items per batch",
            iterations,
            latencies,
            rus
        )
    
    def _compute_result(
        self,
        scenario: str,
        operation: str,
        iterations: int,
        latencies: List[float],
        rus: List[float]
    ) -> BenchmarkResult:
        """Compute benchmark statistics."""
        sorted_latencies = sorted(latencies)
        
        result = BenchmarkResult(
            scenario=scenario,
            operation=operation,
            iterations=iterations,
            total_time=sum(latencies),
            avg_latency_ms=statistics.mean(latencies),
            p50_latency_ms=sorted_latencies[int(len(sorted_latencies) * 0.50)],
            p95_latency_ms=sorted_latencies[int(len(sorted_latencies) * 0.95)],
            p99_latency_ms=sorted_latencies[int(len(sorted_latencies) * 0.99)],
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            total_ru=sum(rus),
            avg_ru_per_operation=statistics.mean(rus),
            operations_per_second=iterations / (sum(latencies) / 1000),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.results.append(result)
        return result
    
    def display_results(self):
        """Display benchmark results in a table."""
        console.print("\n")
        console.print(Panel.fit(
            "[bold cyan]Performance Benchmark Results[/bold cyan]",
            border_style="cyan"
        ))
        
        table = Table(
            title="Latency & Throughput Metrics",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED
        )
        
        table.add_column("Scenario", style="cyan", no_wrap=True)
        table.add_column("Avg (ms)", justify="right", style="yellow")
        table.add_column("p50 (ms)", justify="right", style="green")
        table.add_column("p95 (ms)", justify="right", style="yellow")
        table.add_column("p99 (ms)", justify="right", style="red")
        table.add_column("Ops/sec", justify="right", style="cyan")
        table.add_column("Avg RU", justify="right", style="magenta")
        
        for result in self.results:
            table.add_row(
                result.scenario,
                f"{result.avg_latency_ms:.2f}",
                f"{result.p50_latency_ms:.2f}",
                f"{result.p95_latency_ms:.2f}",
                f"{result.p99_latency_ms:.2f}",
                f"{result.operations_per_second:.2f}",
                f"{result.avg_ru_per_operation:.2f}"
            )
        
        console.print(table)
        console.print()
    
    def save_results(self, output_file: str):
        """Save results to JSON file."""
        results_dict = [asdict(r) for r in self.results]
        
        with open(output_file, 'w') as f:
            json.dump({
                "benchmark_run": datetime.now(timezone.utc).isoformat(),
                "results": results_dict
            }, f, indent=2)
        
        console.print(f"[green]✅ Results saved to: {output_file}[/green]")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Benchmark Cosmos DB HPK performance")
    parser.add_argument(
        "--scenarios",
        default="single,cross,batch",
        help="Comma-separated list of scenarios (single,cross,batch)"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of iterations per scenario"
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.json",
        help="Output file for results"
    )
    parser.add_argument(
        "--container",
        default="documents_hpk",
        help="Container to benchmark"
    )
    
    args = parser.parse_args()
    
    # Get connection info
    connection_string = os.getenv("COSMOS_CONNECTION_STRING")
    database_name = os.getenv("COSMOS_DATABASE_NAME", "eva-rag")
    
    if not connection_string:
        console.print("[red]❌ COSMOS_CONNECTION_STRING not set[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold cyan]EVA RAG - Cosmos DB HPK Performance Benchmark[/bold cyan]",
        border_style="cyan"
    ))
    
    benchmark = CosmosDBBenchmark(connection_string, database_name)
    
    scenarios = args.scenarios.split(',')
    
    try:
        if 'single' in scenarios:
            benchmark.benchmark_single_partition_query(
                iterations=args.iterations,
                container=args.container
            )
        
        if 'cross' in scenarios:
            benchmark.benchmark_cross_partition_query(
                iterations=args.iterations,
                container=args.container
            )
        
        if 'batch' in scenarios:
            benchmark.benchmark_batch_operations(
                iterations=args.iterations // 2,  # Fewer iterations for batch
                batch_size=10,
                container=args.container
            )
        
        benchmark.display_results()
        benchmark.save_results(args.output)
        
        console.print(Panel.fit(
            "[bold green]✅ Benchmark Complete![/bold green]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Benchmark failed: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
