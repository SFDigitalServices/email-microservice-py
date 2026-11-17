"""Pytest configuration and shared fixtures"""
import os
import sys

# Set up a test database URL before importing service modules
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Ensure SENDGRID_API_KEY is set for imports
if not os.environ.get('SENDGRID_API_KEY'):
    os.environ['SENDGRID_API_KEY'] = 'test_key'
