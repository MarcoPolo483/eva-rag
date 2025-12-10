"""
Rollback Script: HPK → Legacy Partition Keys

Rolls back documents from HPK partition (/spaceId/tenantId/userId) to legacy (/tenant_id).

⚠️ WARNING: Use only in emergency situations. Backup data first.

Usage:
    python scripts/rollback_migration.py --dry-run          # Preview rollback
    python scripts/rollback_migration.py --batch-size 100   # Rollback 100 docs
    python scripts/rollback_migration.py --verify-only      # Verify rollback

Requirements:
    - Source container: "documents_hpk" (HPK)
    - Target container: "documents" (legacy)
    - Azure Cosmos DB connection string in environment
"""

import argparse
import logging
import sys
from datetime import datetime, timezone

from azure.cosmos import CosmosClient, PartitionKey, exceptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("rollback.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class RollbackStats:
    """Track rollback statistics."""

    def __init__(self):
        self.total_documents = 0
        self.rolled_back = 0
        self.skipped = 0
        self.failed = 0
        self.start_time = datetime.now(timezone.utc)

    def record_success(self):
        self.rolled_back += 1

    def record_skip(self, doc_id: str):
        self.skipped += 1

    def record_failure(self, doc_id: str, error: str):
        self.failed += 1
        logger.error(f"Failed to rollback {doc_id}: {error}")

    def report(self):
        duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info("ROLLBACK REPORT")
        logger.info("=" * 60)
        logger.info(f"Total documents: {self.total_documents}")
        logger.info(f"Rolled back: {self.rolled_back}")
        logger.info(f"Skipped: {self.skipped}")
        logger.info(f"Failed: {self.failed}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("=" * 60)


def main():
    """Main rollback entry point."""
    parser = argparse.ArgumentParser(description="Rollback HPK migration")
    parser.add_argument("--dry-run", action="store_true", help="Preview rollback")
    parser.add_argument("--batch-size", type=int, default=100, help="Documents per batch")
    parser.add_argument("--connection-string", help="Cosmos DB connection string")
    parser.add_argument("--database", default="eva-rag", help="Database name")
    
    args = parser.parse_args()
    
    logger.warning("⚠️  ROLLBACK OPERATION - This will revert HPK migration")
    
    if not args.dry_run:
        confirm = input("Are you sure you want to proceed? Type 'yes' to confirm: ")
        if confirm.lower() != "yes":
            logger.info("Rollback cancelled")
            sys.exit(0)
    
    # TODO: Implement rollback logic (similar to migration but reversed)
    logger.info("Rollback not yet implemented - backup data manually for now")
    sys.exit(1)


if __name__ == "__main__":
    main()
