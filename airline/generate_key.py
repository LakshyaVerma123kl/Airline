#!/usr/bin/env python3
"""
Script to generate a secure secret key for Flask applications
"""

import secrets
import os

def generate_secret_key(length=32):
    """Generate a cryptographically secure secret key"""
    return secrets.token_hex(length)

def generate_url_safe_key(length=32):
    """Generate a URL-safe secret key"""
    return secrets.token_urlsafe(length)

def generate_multiple_keys():
    """Generate multiple types of secret keys"""
    print("Flask Secret Key Options:")
    print("=" * 50)
    
    print(f"1. Hex Key (64 chars):     {generate_secret_key(32)}")
    print(f"2. URL Safe Key:           {generate_url_safe_key(32)}")
    print(f"3. Short Hex Key:          {generate_secret_key(16)}")
    print(f"4. Long Hex Key:           {generate_secret_key(64)}")
    
    print("\n" + "=" * 50)
    print("Choose any one of these keys for your SECRET_KEY")
    print("Longer keys are more secure!")

if __name__ == "__main__":
    generate_multiple_keys()