#!/usr/bin/env python3
"""Patch a disposable Care360 Patient staging debug checkout using protected CI settings."""
import base64
import os
from pathlib import Path
import re
import subprocess
import sys

ALIAS = "care360-patient-staging"
ORIGINAL = 'android:value="Enter_Your_google_map_key"'
DEBUG = '        debug {\n            applicationIdSuffix ".k3staging"\n        }\n'


def required(name):
    value = os.environ.get(name, "")
    if not value:
        raise ValueError("Missing private CI setting: " + name)
    return value


def prepare(root, scratch):
    api_key = required("K3_STAGING_MAPS_ANDROID_API_KEY")
    expected = required("K3_STAGING_PATIENT_SIGNING_SHA1").strip().upper()
    encoded = required("K3_STAGING_PATIENT_DEBUG_KEYSTORE_B64")
    password = required("K3_STAGING_PATIENT_KEYSTORE_PASSWORD")
    if not re.fullmatch(r"AIza[0-9A-Za-z_-]{35}", api_key):
        raise ValueError("Unexpected staging Maps API key format")
    if not re.fullmatch(r"(?:[0-9A-F]{2}:){19}[0-9A-F]{2}", expected):
        raise ValueError("Expected SHA1 must be 20 colon-separated hex bytes")
    if len(password) < 16:
        raise ValueError("Staging signing password is too short")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ValueError("Staging signing keystore is not valid Base64") from exc
    if not 500 <= len(raw) <= 65536:
        raise ValueError("Staging keystore has unexpected size")

    gradle_file = root / "android/app/build.gradle"
    manifest_file = root / "android/app/src/main/AndroidManifest.xml"
    gradle = gradle_file.read_text(encoding="utf-8")
    manifest = manifest_file.read_text(encoding="utf-8")
    if gradle.count(DEBUG) != 1 or gradle.count("    signingConfigs {\n") != 1:
        raise ValueError("Unexpected Gradle layout; refusing to patch debug signing")
    if manifest.count(ORIGINAL) != 1:
        raise ValueError("Unexpected Maps manifest metadata; refusing to patch")

    scratch.mkdir(parents=True, exist_ok=True)
    keystore = scratch / "care360-patient-staging.p12"
    keystore.write_bytes(raw)
    keystore.chmod(0o600)
    check = subprocess.run([
        "keytool", "-list", "-v", "-storetype", "PKCS12", "-keystore",
        str(keystore), "-alias", ALIAS,
        "-storepass:env", "K3_STAGING_PATIENT_KEYSTORE_PASSWORD",
    ], capture_output=True, text=True, check=False)
    if check.returncode:
        raise ValueError("Staging keystore or alias could not be verified")
    match = re.search(r"(?im)^\s*SHA1:\s*([0-9a-f:]+)\s*$", check.stdout)
    if not match or match.group(1).upper() != expected:
        raise ValueError("Staging signing SHA1 does not match Google Cloud restriction")

    signing = (
        "        k3StagingDebug {\n"
        "            storeFile file(System.getenv('K3_STAGING_PATIENT_KEYSTORE_PATH'))\n"
        "            storePassword System.getenv('K3_STAGING_PATIENT_KEYSTORE_PASSWORD')\n"
        "            keyAlias 'care360-patient-staging'\n"
        "            keyPassword System.getenv('K3_STAGING_PATIENT_KEYSTORE_PASSWORD')\n"
        "        }\n"
    )
    gradle = gradle.replace("    signingConfigs {\n", "    signingConfigs {\n" + signing, 1)
    gradle = gradle.replace(DEBUG,
        "        debug {\n"
        '            applicationIdSuffix ".k3staging"\n'
        "            signingConfig signingConfigs.k3StagingDebug\n"
        '            manifestPlaceholders["K3_STAGING_MAPS_ANDROID_API_KEY"] = System.getenv("K3_STAGING_MAPS_ANDROID_API_KEY")\n'
        "        }\n", 1)
    placeholder = '$' + '{K3_STAGING_MAPS_ANDROID_API_KEY}'
    manifest = manifest.replace(ORIGINAL, 'android:value="' + placeholder + '"', 1)
    gradle_file.write_text(gradle, encoding="utf-8")
    manifest_file.write_text(manifest, encoding="utf-8")
    print("Staging Maps and signing SHA1 verified; debug-only checkout patched.")
    return keystore


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: k3_prepare_patient_maps_signing.py <patient-checkout> <runner-private-dir>", file=sys.stderr)
        sys.exit(2)
    try:
        prepare(Path(sys.argv[1]), Path(sys.argv[2]))
    except (ValueError, OSError) as exc:
        print("Care360 staging Maps setup failed: " + str(exc), file=sys.stderr)
        sys.exit(1)
