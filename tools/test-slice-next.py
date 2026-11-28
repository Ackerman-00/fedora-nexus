#!/usr/bin/env python3
"""Tests for tools/slice-next.py.

Positive and negative cases for the rotation helper: the slice must start at
the recorded next-start, wrap at the end of the inventory, reach the size the
four-run contract needs, and refuse a slice that leaves packages out.
"""
import importlib.util
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    spec = importlib.util.spec_from_file_location("slice_next", os.path.join(HERE, "slice-next.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = load()


class InventoryTest(unittest.TestCase):
    def test_reads_specs_named_after_their_directory(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ("alpha", "beta"):
                os.makedirs(os.path.join(root, name))
                open(os.path.join(root, name, name + ".spec"), "w").close()
            # a spec whose name does not match its directory is not a package
            os.makedirs(os.path.join(root, "gamma"))
            open(os.path.join(root, "gamma", "other.spec"), "w").close()
            self.assertEqual(S.inventory(root), ["alpha", "beta"])


class LedgerTest(unittest.TestCase):
    def test_reads_the_newest_line_and_its_next_start(self):
        text = ("teardown-slice: a b c | next-start: d\n"
                "teardown-slice: x y z | next-start: fluxer\n")
        self.assertEqual(S.ledger(text), (["x", "y", "z"], "fluxer"))

    def test_missing_line_is_empty_not_an_error(self):
        self.assertEqual(S.ledger("run_id: 1\n"), ([], None))

    def test_next_start_absent(self):
        self.assertEqual(S.ledger("teardown-slice: a b |\n"), (["a", "b"], None))


class SliceTest(unittest.TestCase):
    def test_starts_at_next_start_and_wraps(self):
        pkgs = ["a", "b", "c", "d"]
        self.assertEqual(S.next_slice(pkgs, "c", 3), ["c", "d", "a"])
        self.assertEqual(S.following(pkgs, ["c", "d", "a"]), "b")

    def test_unknown_start_falls_back_to_the_first_package(self):
        self.assertEqual(S.next_slice(["a", "b"], "nope", 2), ["a", "b"])

    def test_size_never_exceeds_the_inventory(self):
        self.assertEqual(len(S.next_slice(["a", "b"], "a", 9)), 2)

    def test_min_slice_covers_the_fleet_in_four_runs(self):
        self.assertEqual(S.min_slice(74), 19)
        self.assertEqual(S.min_slice(1), 1)
        self.assertGreaterEqual(S.min_slice(74) * 4, 74)


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.names = ["pkg%02d" % i for i in range(8)]
        for name in self.names:
            os.makedirs(os.path.join(self.root, name))
            open(os.path.join(self.root, name, name + ".spec"), "w").close()
        self.relay = os.path.join(self.root, "relay.md")
        with open(self.relay, "w") as fh:
            fh.write("teardown-slice: pkg00 pkg01 | next-start: pkg02\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_resumes_at_the_recorded_next_start(self):
        rc = S.main(["--root", self.root, "--relay", self.relay, "--list"])
        self.assertEqual(rc, 0)

    def test_check_rejects_a_short_slice(self):
        self.assertEqual(S.main(["--root", self.root, "--relay", self.relay, "--check", "pkg00"]), 1)

    def test_check_accepts_a_full_slice(self):
        self.assertEqual(
            S.main(["--root", self.root, "--relay", self.relay, "--check", " ".join(self.names)]), 0)

    def test_check_rejects_an_unknown_package(self):
        self.assertEqual(
            S.main(["--root", self.root, "--relay", self.relay,
                    "--check", " ".join(self.names) + " ghost"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
