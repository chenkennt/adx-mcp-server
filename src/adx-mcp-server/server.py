#!/usr/bin/env python

import os
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

import dotenv
from mcp.server.fastmcp import FastMCP
from azure.identity import ClientSecretCredential
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder

dotenv.load_dotenv()
mcp = FastMCP("Azure Data Explorer MCP")

@dataclass
class ADXConfig:
    cluster_url: str
    database: str
    # Optional credentials
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

config = ADXConfig(
    cluster_url=os.environ.get("ADX_CLUSTER_URL", ""),
    database=os.environ.get("ADX_DATABASE", ""),
    tenant_id=os.environ.get("AZURE_TENANT_ID", ""),
    client_id=os.environ.get("AZURE_CLIENT_ID", ""),
    client_secret=os.environ.get("AZURE_CLIENT_SECRET", ""),
)

def get_kusto_client() -> KustoClient:
    if not all([config.tenant_id, config.client_id, config.client_secret]):
        raise ValueError("Client credentials are missing. Please set AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET environment variables.")

    credential = ClientSecretCredential(
        tenant_id=config.tenant_id,
        client_id=config.client_id,
        client_secret=config.client_secret
    )
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
        connection_string=config.cluster_url,
        aad_app_id=config.client_id,
        app_key=config.client_secret,
        authority_id=config.tenant_id
    )
    return KustoClient(kcsb)

def format_query_results(result_set) -> List[Dict[str, Any]]:
    if not result_set or not result_set.primary_results:
        return []
    
    primary_result = result_set.primary_results[0]
    columns = [col.column_name for col in primary_result.columns]
    
    formatted_results = []
    for row in primary_result.rows:
        record = {}
        for i, value in enumerate(row):
            record[columns[i]] = value
        formatted_results.append(record)
    
    return formatted_results

@mcp.tool(description="Executes a Kusto Query Language (KQL) query against the configured Azure Data Explorer database and returns the results as a list of dictionaries.")
async def execute_query(query: str) -> List[Dict[str, Any]]:
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

@mcp.tool(description="Retrieves a list of all tables available in the configured Azure Data Explorer database, including their names, folders, and database associations.")
async def list_tables() -> List[Dict[str, Any]]:
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = ".show tables | project TableName, Folder, DatabaseName"
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

@mcp.tool(description="Retrieves the schema information for a specified table in the Azure Data Explorer database, including column names, data types, and other schema-related metadata.")
async def get_table_schema(table_name: str) -> List[Dict[str, Any]]:
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = f".show table {table_name} | getschema"
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

@mcp.tool(description="Retrieves a random sample of rows from the specified table in the Azure Data Explorer database. The sample_size parameter controls how many rows to return (default: 10).")
async def sample_table_data(table_name: str, sample_size: int = 10) -> List[Dict[str, Any]]:
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = f"{table_name} | sample {sample_size}"
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

if __name__ == "__main__":
    print(f"Starting Azure Data Explorer MCP Server...")
    mcp.run()
