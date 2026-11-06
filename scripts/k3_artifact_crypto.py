#!/usr/bin/env python3
"""Authenticated encryption for public CI artifact transport.

Format: K3E1 || 16-byte salt || 12-byte GCM nonce || AES-256-GCM ciphertext+tag.
The 32+ character password is read from an environment variable, not CLI args.
No private build material should be uploaded to public Actions unencrypted.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

MAGIC = b"K3E1"
AAD = b"Care360 synthetic Android debug artifact v1"
ITERATIONS = 600_000


def key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS
    )
    return kdf.derive(password.encode("utf-8"))


def transform(data: bytes, password: str, decrypt: bool) -> bytes:
    if len(password) < 32:
        raise ValueError("Use a randomly generated encryption password of 32+ characters")
    if decrypt:
        if not data.startswith(MAGIC) or len(data) <= 32:
            raise ValueError("Unrecognized or incomplete Care360 encrypted artifact")
        salt = data[4:20]
        nonce = data[20:32]
        return AESGCM(key_from_password(password, salt)).decrypt(
            nonce, data[32:], AAD
        )
    salt, nonce = os.urandom(16), os.urandom(12)
    ciphertext = AESGCM(key_from_password(password, salt)).encrypt(
        nonce, data, AAD
    )
    return MAGIC + salt + nonce + ciphertext


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--encrypt", action="store_true")
    mode.add_argument("--decrypt", action="store_true")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    password = os.environ.get("K3_BUILD_OUTPUT_PASSWORD", "")
    if not password:
        print("Missing K3_BUILD_OUTPUT_PASSWORD environment variable", file=sys.stderr)
        return 2
    if not args.input.is_file():
        print("Input file does not exist", file=sys.stderr)
        return 2
    if args.input.resolve() == args.output.resolve():
        print("Input and output must be different files", file=sys.stderr)
        return 2
    try:
        output = transform(args.input.read_bytes(), password, args.decrypt)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(output)
    except Exception as exc:
        print("Encryption/decryption failed: " + type(exc).__name__, file=sys.stderr)
        return 1
    print("Care360 artifact " + ("decrypted" if args.decrypt else "encrypted") + " successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
