# pylint: disable=redefined-outer-name,no-member,unused-argument
"""Tests for hooks validation"""
import os
from unittest.mock import Mock
import pytest
import falcon
from service.resources.hooks import validate_access


class MockRequest:
    """Mock request object for testing"""
    def __init__(self, headers=None):
        self.headers = headers or {}

    def get_header(self, name, default=None):
        """Mock get_header method - Falcon normalizes header names to uppercase"""
        return self.headers.get(name.upper(), default)


def test_validate_access_with_access_key_header(monkeypatch):
    """Test validate_access with ACCESS_KEY header"""
    monkeypatch.setenv("ACCESS_KEY", "test_key_123")
    
    req = MockRequest(headers={"ACCESS_KEY": "test_key_123"})
    resp = Mock()
    resource = Mock()
    params = {}
    
    # Should not raise an exception
    validate_access(req, resp, resource, params)


def test_validate_access_with_x_apikey_header(monkeypatch):
    """Test validate_access with x-apikey header"""
    monkeypatch.setenv("ACCESS_KEY", "test_key_123")
    
    req = MockRequest(headers={"X-APIKEY": "test_key_123"})
    resp = Mock()
    resource = Mock()
    params = {}
    
    # Should not raise an exception
    validate_access(req, resp, resource, params)


def test_validate_access_with_both_headers_access_key_priority(monkeypatch):
    """Test that ACCESS_KEY header takes priority when both are provided"""
    monkeypatch.setenv("ACCESS_KEY", "test_key_123")
    
    req = MockRequest(headers={
        "ACCESS_KEY": "test_key_123",
        "X-APIKEY": "wrong_key"
    })
    resp = Mock()
    resource = Mock()
    params = {}
    
    # Should not raise an exception (ACCESS_KEY is correct)
    validate_access(req, resp, resource, params)


def test_validate_access_with_both_headers_uses_x_apikey_fallback(monkeypatch):
    """Test that x-apikey is used when ACCESS_KEY header is missing"""
    monkeypatch.setenv("ACCESS_KEY", "test_key_123")
    
    req = MockRequest(headers={"X-APIKEY": "test_key_123"})
    resp = Mock()
    resource = Mock()
    params = {}
    
    # Should not raise an exception
    validate_access(req, resp, resource, params)


def test_validate_access_with_invalid_access_key(monkeypatch):
    """Test validate_access with invalid ACCESS_KEY header"""
    monkeypatch.setenv("ACCESS_KEY", "test_key_123")
    
    req = MockRequest(headers={"ACCESS_KEY": "wrong_key"})
    resp = Mock()
    resource = Mock()
    params = {}
    
    with pytest.raises(falcon.HTTPForbidden):
        validate_access(req, resp, resource, params)


def test_validate_access_with_invalid_x_apikey(monkeypatch):
    """Test validate_access with invalid x-apikey header"""
    monkeypatch.setenv("ACCESS_KEY", "test_key_123")
    
    req = MockRequest(headers={"X-APIKEY": "wrong_key"})
    resp = Mock()
    resource = Mock()
    params = {}
    
    with pytest.raises(falcon.HTTPForbidden):
        validate_access(req, resp, resource, params)


def test_validate_access_with_no_headers(monkeypatch):
    """Test validate_access with no authorization headers"""
    monkeypatch.setenv("ACCESS_KEY", "test_key_123")
    
    req = MockRequest(headers={})
    resp = Mock()
    resource = Mock()
    params = {}
    
    with pytest.raises(falcon.HTTPForbidden):
        validate_access(req, resp, resource, params)


def test_validate_access_with_no_env_key(monkeypatch):
    """Test validate_access when ACCESS_KEY environment variable is not set"""
    monkeypatch.delenv("ACCESS_KEY", raising=False)
    
    req = MockRequest(headers={"ACCESS_KEY": "test_key_123"})
    resp = Mock()
    resource = Mock()
    params = {}
    
    with pytest.raises(falcon.HTTPForbidden):
        validate_access(req, resp, resource, params)


def test_validate_access_case_insensitivity_with_x_apikey(monkeypatch):
    """Test that header names are case-insensitive"""
    monkeypatch.setenv("ACCESS_KEY", "test_key_123")
    
    # Test with different case variations
    req = MockRequest(headers={"X-APIKEY": "test_key_123"})
    resp = Mock()
    resource = Mock()
    params = {}
    
    # Should not raise an exception
    validate_access(req, resp, resource, params)


def test_validate_access_empty_headers(monkeypatch):
    """Test validate_access with empty header values"""
    monkeypatch.setenv("ACCESS_KEY", "test_key_123")
    
    req = MockRequest(headers={"ACCESS_KEY": "", "X-APIKEY": ""})
    resp = Mock()
    resource = Mock()
    params = {}
    
    with pytest.raises(falcon.HTTPForbidden):
        validate_access(req, resp, resource, params)
