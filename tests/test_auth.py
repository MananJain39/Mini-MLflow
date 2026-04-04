"""Tests for API key authentication."""

import pytest


class TestAuthenticationBypass:
    def test_auth_no_keys_configured(self, api_client, monkeypatch):
        """When API_KEYS is unset, auth is bypassed (MVP mode)."""
        monkeypatch.setenv("API_KEYS", "")
        resp = api_client.post("/api/experiments/set", json={"name": "no-auth-exp"})
        assert resp.status_code == 200


class TestAuthenticationWithKeys:
    def test_auth_valid_key(self, api_client, monkeypatch):
        """Valid API key in X-API-Key header grants access."""
        monkeypatch.setenv("API_KEYS", "secret123")
        api_client.headers.update({"X-API-Key": "secret123"})
        resp = api_client.post("/api/experiments/set", json={"name": "auth-exp"})
        assert resp.status_code == 200

    def test_auth_invalid_key(self, api_client, monkeypatch):
        """Invalid API key returns 401 Unauthorized."""
        monkeypatch.setenv("API_KEYS", "secret123")
        api_client.headers.update({"X-API-Key": "wrongkey"})
        resp = api_client.post("/api/experiments/set", json={"name": "fail-exp"})
        assert resp.status_code == 401
        assert "Invalid or missing API Key" in resp.json()["detail"]

    def test_auth_missing_key(self, api_client, monkeypatch):
        """Missing X-API-Key header when keys are configured returns 401."""
        monkeypatch.setenv("API_KEYS", "secret123")
        resp = api_client.post("/api/experiments/set", json={"name": "fail-exp-2"})
        assert resp.status_code == 401
        assert "Invalid or missing API Key" in resp.json()["detail"]

    def test_auth_multiple_valid_keys(self, api_client, monkeypatch):
        """Multiple keys (comma-separated) can authenticate."""
        monkeypatch.setenv("API_KEYS", "secret1, secret2, secret3")
        api_client.headers.update({"X-API-Key": "secret2"})
        resp = api_client.post("/api/experiments/set", json={"name": "multi-key-exp"})
        assert resp.status_code == 200
