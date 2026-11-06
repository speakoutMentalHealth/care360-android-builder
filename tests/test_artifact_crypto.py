import os
import unittest

from scripts.k3_artifact_crypto import MAGIC, transform


class CryptoTransportTests(unittest.TestCase):
    def setUp(self):
        self.password = "a-long-test-only-secret-at-least-thirty-two-chars"

    def test_authenticated_roundtrip(self):
        original = b"synthetic non-sensitive Care360 example" * 500
        ciphertext = transform(original, self.password, decrypt=False)
        self.assertTrue(ciphertext.startswith(MAGIC))
        self.assertNotIn(original[:100], ciphertext)
        self.assertEqual(original, transform(ciphertext, self.password, decrypt=True))

    def test_wrong_password_is_rejected(self):
        ciphertext = transform(b"dummy", self.password, decrypt=False)
        with self.assertRaises(Exception):
            transform(ciphertext, self.password + "changed", decrypt=True)

    def test_tampered_ciphertext_is_rejected(self):
        ciphertext = bytearray(transform(b"dummy", self.password, decrypt=False))
        ciphertext[-1] ^= 1
        with self.assertRaises(Exception):
            transform(bytes(ciphertext), self.password, decrypt=True)

    def test_short_password_is_rejected(self):
        with self.assertRaises(ValueError):
            transform(b"dummy", "short", decrypt=False)


if __name__ == "__main__":
    unittest.main()
