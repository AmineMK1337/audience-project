"""Utilities for initializing and accessing Google Firestore."""

from __future__ import annotations

import os
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, firestore


@lru_cache(maxsize=1)
def _get_app() -> firebase_admin.App:
    """Initialise and memoise the default Firebase app."""
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise RuntimeError(
            "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set."
        )
    if not os.path.isfile(cred_path):
        raise FileNotFoundError(f"Service account file not found: {cred_path}")

    cred = credentials.Certificate(cred_path)
    return firebase_admin.initialize_app(cred)


def get_firestore_client() -> firestore.Client:
    """Return a Firestore client tied to the cached Firebase app."""
    app = _get_app()
    return firestore.client(app)
