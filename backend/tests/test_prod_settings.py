"""Production settings regressions."""

from __future__ import annotations

import importlib


def test_prod_settings_reads_public_hosts_from_env(monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", "tablesched.example.com,api.tablesched.example.com")
    monkeypatch.setenv("PUBLIC_DOMAIN", "tablesched.example.com")

    from config.settings import prod

    importlib.reload(prod)

    assert prod.ALLOWED_HOSTS == ["tablesched.example.com", "api.tablesched.example.com"]
    assert prod.PUBLIC_DOMAIN == "tablesched.example.com"
