"""
Audit Service for EVA RAG - System-level tamper-evident audit trail.

This service implements:
1. Sequential numbering (atomic counter)
2. System-level hash chain (global, not per-user)
3. Dual-write to Cosmos DB + Azure Immutable Blob Storage
4. Chain verification for tamper-evidence
"""

import hashlib
import json
from typing import Optional

from azure.cosmos import ContainerProxy, CosmosClient, PartitionKey
from azure.storage.blob import BlobServiceClient

from eva_rag.models.audit_log import AuditLog, AuditLogSummary


class AuditService:
    """
    Service for managing system-level audit logs with tamper-evidence.

    Key features:
    - Sequential numbering via atomic counter
    - System-level hash chain (not per-user, global sequence)
    - Dual-write to Cosmos DB + Azure Immutable Blob Storage
    - Immutable (no updates/deletes)
    - Chain verification for tamper detection
    """

    def __init__(
        self,
        cosmos_client: CosmosClient,
        database_name: str,
        blob_service_client: Optional[BlobServiceClient] = None,
        immutable_container_name: str = "audit-logs",
    ):
        """
        Initialize the Audit Service.

        Args:
            cosmos_client: Cosmos DB client
            database_name: Database name
            blob_service_client: Optional Azure Blob client for immutable storage
            immutable_container_name: Container name for immutable blobs
        """
        self.cosmos_client = cosmos_client
        self.database_name = database_name
        self.blob_service_client = blob_service_client
        self.immutable_container_name = immutable_container_name

        # Get or create database
        self.database = self.cosmos_client.get_database_client(database_name)

        # Get or create audit_logs container
        # Partition key: /sequence_number (sequential, not HPK)
        try:
            self.container: ContainerProxy = self.database.create_container_if_not_exists(
                id="audit_logs",
                partition_key=PartitionKey(path="/sequence_number"),
            )
        except Exception as e:
            # Container might already exist
            self.container: ContainerProxy = self.database.get_container_client("audit_logs")

        # Get or create counter container (for atomic sequence generation)
        try:
            self.counter_container: ContainerProxy = self.database.create_container_if_not_exists(
                id="audit_counters",
                partition_key=PartitionKey(path="/id"),
            )
        except Exception:
            self.counter_container: ContainerProxy = self.database.get_container_client("audit_counters")

        # Initialize blob container for immutable storage
        if self.blob_service_client:
            self.blob_container = self.blob_service_client.get_blob_service_client().get_container_client(
                immutable_container_name
            )
            # Ensure container exists with immutable policy
            try:
                self.blob_container.create_container()
            except Exception:
                pass  # Container might already exist

    def _get_next_sequence_number(self) -> int:
        """
        Get next sequence number using atomic increment.

        Returns:
            Next sequence number
        """
        counter_id = "audit_sequence"

        # Try to increment existing counter
        try:
            # Read current counter
            counter_item = self.counter_container.read_item(item=counter_id, partition_key=counter_id)
            current_value = counter_item["value"]

            # Increment using optimistic concurrency (etag)
            counter_item["value"] = current_value + 1
            self.counter_container.replace_item(item=counter_item, body=counter_item, etag=counter_item["_etag"])

            return current_value + 1

        except Exception:
            # Counter doesn't exist, create it
            counter_item = {"id": counter_id, "value": 1}
            try:
                self.counter_container.create_item(body=counter_item)
                return 1
            except Exception:
                # Race condition: another process created counter, retry
                return self._get_next_sequence_number()

    def _compute_content_hash(self, log: AuditLog) -> str:
        """
        Compute SHA-256 hash of audit log content.

        Hash includes: id, sequence_number, event_type, event_data, timestamp, previous_hash

        Args:
            log: Audit log entry

        Returns:
            SHA-256 hash (hex string)
        """
        content = (
            f"{log.id}|"
            f"{log.sequence_number}|"
            f"{log.event_type}|"
            f"{log.event_category}|"
            f"{json.dumps(log.event_data, sort_keys=True)}|"
            f"{log.timestamp.isoformat()}|"
            f"{log.previous_hash}"
        )
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_latest_audit_log(self) -> Optional[AuditLog]:
        """
        Get the latest audit log entry (highest sequence_number).

        Returns:
            Latest audit log, or None if no logs exist
        """
        query = "SELECT * FROM c ORDER BY c.sequence_number DESC OFFSET 0 LIMIT 1"
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))

        if not items:
            return None

        return AuditLog(**items[0])

    def create_audit_log(self, log: AuditLog) -> AuditLog:
        """
        Create a new audit log entry with hash chain.

        This method:
        1. Assigns next sequence_number
        2. Gets previous log's hash (or "genesis" for first)
        3. Computes content_hash
        4. Writes to Cosmos DB
        5. Optionally writes to Azure Immutable Blob Storage

        Args:
            log: Audit log entry (sequence_number, content_hash, previous_hash will be set)

        Returns:
            Created audit log with populated fields
        """
        # Get next sequence number
        log.sequence_number = self._get_next_sequence_number()

        # Get previous hash (or "genesis" for first log)
        latest_log = self.get_latest_audit_log()
        if latest_log and latest_log.sequence_number < log.sequence_number:
            log.previous_hash = latest_log.content_hash
        else:
            log.previous_hash = "genesis"

        # Compute content hash
        log.content_hash = self._compute_content_hash(log)

        # Write to Cosmos DB
        log_dict = log.model_dump(mode="json")
        self.container.create_item(body=log_dict)

        # Write to Azure Immutable Blob Storage (if configured)
        if self.blob_service_client:
            blob_name = f"{log.sequence_number:010d}.json"
            blob_client = self.blob_container.get_blob_client(blob_name)

            blob_client.upload_blob(
                data=json.dumps(log_dict, indent=2),
                overwrite=False,  # Immutable: do not overwrite
            )

            log.immutable_blob_url = blob_client.url

            # Update Cosmos DB entry with blob URL
            log_dict["immutable_blob_url"] = log.immutable_blob_url
            self.container.replace_item(item=log_dict, body=log_dict)

        return log

    def get_audit_log(self, sequence_number: int) -> Optional[AuditLog]:
        """
        Get a specific audit log by sequence number.

        Args:
            sequence_number: Sequence number (partition key)

        Returns:
            Audit log, or None if not found
        """
        try:
            item = self.container.read_item(item=str(sequence_number), partition_key=sequence_number)
            return AuditLog(**item)
        except Exception:
            return None

    def list_audit_logs(
        self,
        space_id: Optional[str] = None,
        event_type: Optional[str] = None,
        event_category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogSummary]:
        """
        List audit logs with optional filters.

        Args:
            space_id: Filter by Space ID (optional)
            event_type: Filter by event type (optional)
            event_category: Filter by event category (optional)
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of audit log summaries
        """
        query_parts = ["SELECT c.id, c.sequence_number, c.event_type, c.event_category, c.timestamp, c.space_id, c.tenant_id, c.user_id FROM c"]
        where_clauses = []

        if space_id:
            where_clauses.append(f"c.space_id = '{space_id}'")
        if event_type:
            where_clauses.append(f"c.event_type = '{event_type}'")
        if event_category:
            where_clauses.append(f"c.event_category = '{event_category}'")

        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))

        query_parts.append(f"ORDER BY c.sequence_number DESC OFFSET {skip} LIMIT {limit}")
        query = " ".join(query_parts)

        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        return [AuditLogSummary(**item) for item in items]

    def verify_audit_chain(self, count: int = 1000) -> tuple[bool, str]:
        """
        Verify the integrity of the audit log hash chain.

        This walks through the latest `count` logs in chronological order and verifies:
        1. Each log's previous_hash matches the previous log's content_hash
        2. Each log's content_hash is correctly computed

        Args:
            count: Number of recent logs to verify

        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if chain is valid
            - (False, "error details") if chain is broken
        """
        # Get latest logs in chronological order (oldest first)
        query = f"SELECT * FROM c ORDER BY c.sequence_number ASC OFFSET 0 LIMIT {count}"
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))

        if not items:
            return (True, "")  # No logs to verify

        expected_previous_hash = "genesis"

        for item in items:
            log = AuditLog(**item)

            # Verify previous_hash linkage
            if log.previous_hash != expected_previous_hash:
                return (
                    False,
                    f"Hash chain broken at sequence {log.sequence_number}: "
                    f"expected previous_hash='{expected_previous_hash}', "
                    f"got '{log.previous_hash}'",
                )

            # Verify content_hash
            computed_hash = self._compute_content_hash(log)
            if computed_hash != log.content_hash:
                return (
                    False,
                    f"Content hash mismatch at sequence {log.sequence_number}: "
                    f"expected '{log.content_hash}', computed '{computed_hash}'",
                )

            # Update expected for next iteration
            expected_previous_hash = log.content_hash

        return (True, "")
