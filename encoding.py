# coding=utf-8
import hashlib

from serialize import bytes_as_revhex


def double_sha256(data):
    """A standard compound hash."""
    return bytes_as_revhex(hashlib.sha256(hashlib.sha256(data).digest()).digest())
