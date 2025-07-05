#!/usr/bin/env python3

import os

from app.config import settings

print("=== Configuration Debug ===")
print(f"DATABASE_URL env var: {os.getenv('DATABASE_URL', 'Not set')}")
print(f"Settings database_url: {settings.database_url}")
print(f"Settings debug: {settings.debug}")
print("===========================")
