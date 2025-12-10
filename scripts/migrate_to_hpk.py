"""
Data Migration Script: Legacy → HPK Partition Keys

Migrates documents from legacy partition key (/tenant_id) to new HPK (/spaceId/tenantId/userId).

Usage:
    python scripts/migrate_to_hpk.py --dry-run          # Preview migration
    python scripts/migrate_to_hpk.py --batch-size 100   # Migrate 100 docs at a time
    python scripts/migrate_to_hpk.py --verify-only      # Verify migrated data

Requirements:
    - Source container: "documents" (legacy)
    - Target container: "documents_hpk" (new)
    - Azure Cosmos DB connection string in environment
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from azure.cosmos import CosmosClient, PartitionKey, exceptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("migration.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class MigrationStats:
    """Track migration statistics."""

    def __init__(self):
        self.total_documents = 0
        self.migrated = 0
        self.skipped = 0
        self.failed = 0
        self.errors = []
        self.start_time = datetime.now(timezone.utc)

    def record_success(self):
        self.migrated += 1

    def record_skip(self, doc_id: str, reason: str):
        self.skipped += 1
        logger.warning(f"Skipped document {doc_id}: {reason}")

    def record_failure(self, doc_id: str, error: str):
        self.failed += 1
        self.errors.append({"doc_id": doc_id, "error": error})
        logger.error(f"Failed to migrate document {doc_id}: {error}")

    def report(self):
        """Generate migration report."""
        duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info("MIGRATION REPORT")
        logger.info("=" * 60)
        logger.info(f"Total documents: {self.total_documents}")
        logger.info(f"Successfully migrated: {self.migrated}")
        logger.info(f"Skipped (already migrated): {self.skipped}")
        logger.info(f"Failed: {self.failed}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Rate: {self.migrated / duration:.2f} docs/second" if duration > 0 else "N/A")
        
        if self.errors:
            logger.error(f"\nErrors encountered: {len(self.errors)}")
            for error in self.errors[:10]:  # Show first 10 errors
                logger.error(f"  - {error['doc_id']}: {error['error']}")
            if len(self.errors) > 10:
                logger.error(f"  ... and {len(self.errors) - 10} more errors")
        
        logger.info("=" * 60)


class DocumentMigration:
    """Handle migration from legacy to HPK partition keys."""

    def __init__(
        self,
        cosmos_client: CosmosClient,
        database_name: str,
        source_container: str = "documents",
        target_container: str = "documents_hpk",
    ):
        self.cosmos_client = cosmos_client
        self.database_name = database_name
        self.source_container_name = source_container
        self.target_container_name = target_container
        
        # Get database
        self.database = cosmos_client.get_database_client(database_name)
        
        # Get or create containers
        self.source_container = self.database.get_container_client(source_container)
        
        try:
            self.target_container = self.database.create_container_if_not_exists(
                id=target_container,
                partition_key=PartitionKey(
                    path=["/space_id", "/tenant_id", "/user_id"],
                    kind="MultiHash"
                ),
            )
            logger.info(f"Target container '{target_container}' ready with HPK")
        except Exception as e:
            logger.error(f"Failed to create target container: {e}")
            raise

    def _compute_document_hash(self, doc: dict[str, Any]) -> str:
        """Compute SHA-256 hash of document content for verification."""
        # Sort keys for consistent hashing
        content = json.dumps(doc, sort_keys=True)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _validate_document(self, doc: dict[str, Any]) -> tuple[bool, str]:
        """Validate document has required fields for HPK migration."""
        required_fields = ["id", "space_id", "tenant_id", "user_id"]
        
        missing = [f for f in required_fields if f not in doc or doc[f] is None]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        # Validate UUIDs
        for field in ["id", "space_id", "tenant_id", "user_id"]:
            try:
                UUID(str(doc[field]))
            except (ValueError, AttributeError):
                return False, f"Invalid UUID in field: {field}"
        
        return True, ""

    def _document_exists_in_target(self, doc_id: str, space_id: str, tenant_id: str, user_id: str) -> bool:
        """Check if document already exists in target container."""
        try:
            self.target_container.read_item(
                item=doc_id,
                partition_key=[space_id, tenant_id, user_id]
            )
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
        except Exception as e:
            logger.warning(f"Error checking document existence: {e}")
            return False

    def migrate_document(self, doc: dict[str, Any], force: bool = False) -> tuple[bool, str]:
        """
        Migrate a single document from source to target.
        
        Returns:
            (success: bool, message: str)
        """
        doc_id = doc.get("id")
        
        # Validate document
        is_valid, error = self._validate_document(doc)
        if not is_valid:
            return False, error
        
        space_id = str(doc["space_id"])
        tenant_id = str(doc["tenant_id"])
        user_id = str(doc["user_id"])
        
        # Check if already migrated
        if not force and self._document_exists_in_target(doc_id, space_id, tenant_id, user_id):
            return False, "Already migrated"
        
        # Compute hash for verification
        source_hash = self._compute_document_hash(doc)
        doc["_migration_metadata"] = {
            "migrated_at": datetime.now(timezone.utc).isoformat(),
            "source_hash": source_hash,
            "migration_version": "1.0",
        }
        
        # Insert into target container
        try:
            self.target_container.upsert_item(body=doc)
            logger.debug(f"Migrated document {doc_id} to HPK container")
            return True, "Success"
        except Exception as e:
            return False, f"Failed to insert: {str(e)}"

    def migrate_batch(
        self,
        batch_size: int = 100,
        skip: int = 0,
        dry_run: bool = False,
        force: bool = False,
    ) -> MigrationStats:
        """
        Migrate documents in batches.
        
        Args:
            batch_size: Number of documents per batch
            skip: Number of documents to skip
            dry_run: If True, only preview migration
            force: If True, overwrite existing documents
        
        Returns:
            MigrationStats object with results
        """
        stats = MigrationStats()
        
        logger.info(f"Starting migration (batch_size={batch_size}, skip={skip}, dry_run={dry_run})")
        
        # Query source container (legacy partition key)
        query = f"SELECT * FROM c OFFSET {skip} LIMIT {batch_size}"
        
        try:
            items = list(self.source_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            stats.total_documents = len(items)
            
            logger.info(f"Found {len(items)} documents to migrate")
            
            if dry_run:
                logger.info("DRY RUN - No documents will be migrated")
                for item in items:
                    doc_id = item.get("id", "unknown")
                    is_valid, error = self._validate_document(item)
                    if is_valid:
                        logger.info(f"  ✓ Would migrate: {doc_id}")
                        stats.record_success()
                    else:
                        logger.warning(f"  ✗ Would skip: {doc_id} - {error}")
                        stats.record_skip(doc_id, error)
                return stats
            
            # Migrate each document
            for item in items:
                doc_id = item.get("id", "unknown")
                success, message = self.migrate_document(item, force=force)
                
                if success:
                    stats.record_success()
                    logger.info(f"✓ Migrated: {doc_id}")
                elif message == "Already migrated":
                    stats.record_skip(doc_id, message)
                else:
                    stats.record_failure(doc_id, message)
        
        except Exception as e:
            logger.error(f"Migration batch failed: {e}")
            stats.record_failure("BATCH", str(e))
        
        return stats

    def verify_migration(self, sample_size: int = 100) -> tuple[int, int]:
        """
        Verify migrated documents match source.
        
        Returns:
            (verified_count, error_count)
        """
        logger.info(f"Verifying migration (sample_size={sample_size})")
        
        verified = 0
        errors = 0
        
        # Query source container
        query = f"SELECT * FROM c OFFSET 0 LIMIT {sample_size}"
        source_items = list(self.source_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        for source_doc in source_items:
            doc_id = source_doc.get("id")
            space_id = str(source_doc.get("space_id"))
            tenant_id = str(source_doc.get("tenant_id"))
            user_id = str(source_doc.get("user_id"))
            
            try:
                # Read from target
                target_doc = self.target_container.read_item(
                    item=doc_id,
                    partition_key=[space_id, tenant_id, user_id]
                )
                
                # Compare key fields
                key_fields = ["id", "space_id", "tenant_id", "user_id", "filename"]
                for field in key_fields:
                    if source_doc.get(field) != target_doc.get(field):
                        logger.error(f"Mismatch in {field} for doc {doc_id}")
                        errors += 1
                        break
                else:
                    verified += 1
                    logger.debug(f"✓ Verified: {doc_id}")
            
            except exceptions.CosmosResourceNotFoundError:
                logger.error(f"Document {doc_id} not found in target")
                errors += 1
            except Exception as e:
                logger.error(f"Verification error for {doc_id}: {e}")
                errors += 1
        
        logger.info(f"Verification complete: {verified} verified, {errors} errors")
        return verified, errors


def main():
    """Main migration entry point."""
    parser = argparse.ArgumentParser(description="Migrate documents to HPK partition keys")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without making changes")
    parser.add_argument("--batch-size", type=int, default=100, help="Documents per batch (default: 100)")
    parser.add_argument("--skip", type=int, default=0, help="Skip first N documents")
    parser.add_argument("--force", action="store_true", help="Overwrite existing documents")
    parser.add_argument("--verify-only", action="store_true", help="Only verify migration")
    parser.add_argument("--connection-string", help="Cosmos DB connection string (or use env var)")
    parser.add_argument("--database", default="eva-rag", help="Database name (default: eva-rag)")
    
    args = parser.parse_args()
    
    # Get connection string
    import os
    connection_string = args.connection_string or os.getenv("COSMOS_CONNECTION_STRING")
    if not connection_string:
        logger.error("No connection string provided. Use --connection-string or set COSMOS_CONNECTION_STRING env var")
        sys.exit(1)
    
    # Initialize Cosmos client
    try:
        client = CosmosClient.from_connection_string(connection_string)
        logger.info("Connected to Cosmos DB")
    except Exception as e:
        logger.error(f"Failed to connect to Cosmos DB: {e}")
        sys.exit(1)
    
    # Initialize migration
    migration = DocumentMigration(
        cosmos_client=client,
        database_name=args.database,
    )
    
    # Run verification only
    if args.verify_only:
        verified, errors = migration.verify_migration(sample_size=args.batch_size)
        logger.info(f"\nVerification: {verified} verified, {errors} errors")
        sys.exit(0 if errors == 0 else 1)
    
    # Run migration
    stats = migration.migrate_batch(
        batch_size=args.batch_size,
        skip=args.skip,
        dry_run=args.dry_run,
        force=args.force,
    )
    
    # Report results
    stats.report()
    
    # Exit with error code if any failures
    sys.exit(0 if stats.failed == 0 else 1)


if __name__ == "__main__":
    main()
