#!/usr/bin/env python

import pytest
import os
from adx_mcp_server.server import config, ADXConfig

class TestConfig:
    def test_config_initialization(self, monkeypatch):
        """Test that config is initialized correctly from environment variables."""
        # Set environment variables
        monkeypatch.setenv("ADX_CLUSTER_URL", "https://testcluster.region.kusto.windows.net")
        monkeypatch.setenv("ADX_DATABASE", "testdb")
        monkeypatch.setenv("AZURE_TENANT_ID", "test-tenant-id")
        monkeypatch.setenv("AZURE_CLIENT_ID", "test-client-id")
        monkeypatch.setenv("AZURE_CLIENT_SECRET", "test-client-secret")
        
        # Re-initialize the config to pick up the environment variables
        test_config = ADXConfig(
            cluster_url=os.environ.get("ADX_CLUSTER_URL", ""),
            database=os.environ.get("ADX_DATABASE", ""),
            tenant_id=os.environ.get("AZURE_TENANT_ID", ""),
            client_id=os.environ.get("AZURE_CLIENT_ID", ""),
            client_secret=os.environ.get("AZURE_CLIENT_SECRET", ""),
        )
        
        # Verify the config values
        assert test_config.cluster_url == "https://testcluster.region.kusto.windows.net"
        assert test_config.database == "testdb"
        assert test_config.tenant_id == "test-tenant-id"
        assert test_config.client_id == "test-client-id"
        assert test_config.client_secret == "test-client-secret"
    
    def test_missing_config(self, monkeypatch):
        """Test that config handles missing environment variables."""
        # Clear environment variables
        for var in ["ADX_CLUSTER_URL", "ADX_DATABASE", "AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"]:
            monkeypatch.delenv(var, raising=False)
        
        # Re-initialize the config with empty environment
        test_config = ADXConfig(
            cluster_url=os.environ.get("ADX_CLUSTER_URL", ""),
            database=os.environ.get("ADX_DATABASE", ""),
            tenant_id=os.environ.get("AZURE_TENANT_ID", ""),
            client_id=os.environ.get("AZURE_CLIENT_ID", ""),
            client_secret=os.environ.get("AZURE_CLIENT_SECRET", ""),
        )
        
        # Verify the config values are empty
        assert test_config.cluster_url == ""
        assert test_config.database == ""
        assert test_config.tenant_id == ""
        assert test_config.client_id == ""
        assert test_config.client_secret == ""
