#!/usr/bin/env python3
"""Quick script to check document status in Cosmos DB"""
import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = client["eva-rag"]

total = db.documents.count_documents({})
indexed = db.documents.count_documents({"status": "INDEXED"})
embedded = db.documents.count_documents({"status": "EMBEDDED"})
chunked = db.documents.count_documents({"status": "CHUNKED"})
uploaded = db.documents.count_documents({"status": "UPLOADED"})

print(f"📊 Document Status:")
print(f"   Total: {total}")
print(f"   INDEXED: {indexed}")
print(f"   EMBEDDED: {embedded}")
print(f"   CHUNKED: {chunked}")
print(f"   UPLOADED: {uploaded}")

if indexed == 0 and embedded > 0:
    print(f"\n⚠️ Problem: {embedded} documents stuck at EMBEDDED status")
    print("   Expected: Should be INDEXED after ingestion")
    
    # Check a sample document
    sample = db.documents.find_one({"status": "EMBEDDED"})
    if sample:
        print(f"\n   Sample document: {sample.get('file_name')}")
        print(f"   Document ID: {sample.get('_id')}")
