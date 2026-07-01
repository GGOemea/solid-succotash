#!/usr/bin/python3

import argparse

import cryptography.x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

parser = argparse.ArgumentParser()
sub = parser.add_subparsers()
create = sub.add_parser("create")
create.add_argument("--usage", type=int, default=3)
create.add_argument("--selector", type=int, default=1)
create.add_argument("--mtype", type=int, default=1)
create.add_argument("--certificate", required=True)
create.add_argument("--port", type=int, default=443)
create.add_argument("hostname")

args = parser.parse_args()

with open(args.certificate, "rb") as f:
    cert = cryptography.x509.load_pem_x509_certificate(f.read())
assert args.usage in (0, 1, 2, 3)
usage = "{:02x}".format(args.usage)
assert args.selector in (0, 1)
selector = "{:02x}".format(args.selector)
assert args.mtype in (0, 1, 2)
mtype = "{:02x}".format(args.mtype)
if args.selector == 0:
    cert_bytes = cert.public_bytes(Encoding.DER)
elif args.selector == 1:
    cert_bytes = cert.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

if args.mtype == 0:
    hash = cert_bytes
elif args.mtype == 1:
    h = hashes.Hash(hashes.SHA256())
    h.update(cert_bytes)
    hash = h.finalize()
elif args.mtype == 2:
    h = hashes.Hash(hashes.SHA512())
    h.update(cert_bytes)
    hash = h.finalize()

hash = hash.hex()
len = int((len(usage) + len(selector) + len(mtype) + len(hash)) / 2)

print(f"_{args.port}._tcp.{args.hostname}. IN TYPE52 \\# {len} {usage}{selector}{mtype}{hash}")
