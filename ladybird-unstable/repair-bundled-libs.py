#!/usr/bin/env python3
"""Rebuild a libicudata that vcpkg's rpath rewrite left unloadable, then refuse
the build if any bundled library is still corrupt."""

import glob
import os
import re
import struct
import subprocess
import sys
import tempfile

SONAME = 14
LOAD = 1

# a loader that dies in relocation (the vcpkg damage) returns a signal, not a message
CORRUPT = re.compile(r"invalid ELF|file too short|wrong ELF class|not a dynamic"
                     r"|no version information|cannot read file data|bad ELF", re.I)

PROBE = "import ctypes,sys; ctypes.CDLL(sys.argv[1])"


def load_result(path):
    """dlopen in a child so a loader SIGSEGV is a return code, not our death."""
    try:
        done = subprocess.run([sys.executable, "-c", PROBE, path],
                              capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "corrupt", "loader hung"
    if done.returncode == 0:
        return "ok", ""
    if done.returncode < 0 or done.returncode >= 128:
        return "corrupt", "loader died with signal %d" % (
            -done.returncode if done.returncode < 0 else done.returncode - 128)
    message = (done.stderr or done.stdout).strip().splitlines()
    message = message[-1] if message else "unknown error"
    return ("corrupt" if CORRUPT.search(message) else "unresolved"), message


def cstr(data, off):
    return data[off:data.index(b"\0", off)].decode()


class Elf:
    def __init__(self, path):
        self.path = path
        self.data = data = open(path, "rb").read()
        if data[:4] != b"\x7fELF" or data[4] != 2:
            raise ValueError("not ELF64")
        h = struct.unpack_from("<HHIQQQIHHHHHH", data, 16)
        self.phoff, self.shoff = h[4], h[5]
        self.phentsize, self.phnum = h[8], h[9]
        self.shentsize, self.shnum, self.shstrndx = h[10], h[11], h[12]
        self.sections = [struct.unpack_from("<IIQQQQIIQQ", data, self.shoff + i * self.shentsize)
                         for i in range(self.shnum)]
        strtab = self.sections[self.shstrndx]
        self.shnames = [(cstr(data, strtab[4] + s[0]) if s[0] else "") for s in self.sections]
        self.section = {n: s for n, s in zip(self.shnames, self.sections)}

    def segments(self):
        return [struct.unpack_from("<IIQQQQQQ", self.data, self.phoff + i * self.phentsize)
                for i in range(self.phnum)]

    def vaddr_to_off(self, addr, size):
        for p_type, _flags, p_offset, p_vaddr, _paddr, p_filesz, _memsz, _align in self.segments():
            if p_type == LOAD and p_vaddr <= addr and addr + size <= p_vaddr + p_filesz:
                return addr - p_vaddr + p_offset
        raise ValueError("address 0x%x not in any PT_LOAD" % addr)

    def dynamic(self):
        sec = self.section.get(".dynamic")
        if sec is None:
            raise ValueError("no .dynamic")
        out = []
        for i in range(0, sec[5], 16):
            tag, val = struct.unpack_from("<QQ", self.data, sec[4] + i)
            if tag == 0:
                break
            out.append((tag, val))
        return out

    def soname(self):
        """Read DT_SONAME through .dynstr: DT_STRTAB itself is stale on a damaged file."""
        idx = [v for t, v in self.dynamic() if t == SONAME]
        dynstr = self.section[".dynstr"]
        return cstr(self.data, dynstr[4] + idx[0]) if idx else None

    def data_symbol(self):
        """The ICU data blob: a global object named icudt*_dat covering .rodata."""
        dynsym, dynstr = self.section.get(".dynsym"), self.section.get(".dynstr")
        if dynsym is None or dynstr is None:
            raise ValueError("no .dynsym/.dynstr")
        for i in range(dynsym[5] // 24):
            st_name, _info, _other, _shndx, st_value, st_size = struct.unpack_from(
                "<IBBHQQ", self.data, dynsym[4] + i * 24)
            name = cstr(self.data, dynstr[4] + st_name) if st_name else ""
            if name.startswith("icudt") and name.endswith("_dat") and st_size:
                return name, st_value, st_size
        raise ValueError("no icudt*_dat symbol")


def rebuild(elf):
    """Relink the data blob into a fresh shared object, keeping the upstream data."""
    name, addr, size = elf.data_symbol()
    blob = elf.data[elf.vaddr_to_off(addr, size):][:size]
    rodata = elf.section.get(".rodata")
    if rodata and rodata[5] != size:
        raise ValueError("%s is 0x%x bytes but .rodata is 0x%x" % (name, size, rodata[5]))
    soname = elf.soname()
    if not soname:
        raise ValueError("no DT_SONAME")

    with tempfile.TemporaryDirectory() as tmp:
        blob_path = os.path.join(tmp, "data.bin")
        asm_path = os.path.join(tmp, "data.s")
        obj_path = os.path.join(tmp, "data.o")
        out_path = os.path.join(tmp, "out.so")
        open(blob_path, "wb").write(blob)
        open(asm_path, "w").write(
            "\t.section .rodata\n"
            "\t.globl %s\n\t.type %s, @object\n\t.balign 16\n"
            "%s:\n\t.incbin \"%s\"\n\t.size %s, . - %s\n"
            "\t.section .note.GNU-stack,\"\",@progbits\n"
            % (name, name, name, blob_path, name, name))
        subprocess.run(["as", "-o", obj_path, asm_path], check=True)
        subprocess.run(["ld", "-shared", "--soname", soname, "-z", "now", "-Bsymbolic",
                        "--hash-style=gnu", "--build-id=sha1", "-o", out_path, obj_path],
                       check=True)
        os.chmod(out_path, os.stat(elf.path).st_mode)
        os.replace(out_path, elf.path)
    return name


def main():
    libdir = sys.argv[1]
    libs = sorted(p for p in glob.glob(os.path.join(libdir, "*.so*")) if not os.path.islink(p))

    # repair first: every ICU consumer is unloadable until the data blob is valid again
    for path in libs:
        if not os.path.basename(path).startswith("libicudata.so"):
            continue
        state, why = load_result(path)
        if state != "corrupt":
            continue
        try:
            name = rebuild(Elf(path))
        except (ValueError, OSError, subprocess.CalledProcessError) as error:
            print("%s: rebuild failed: %s" % (path, error), file=sys.stderr)
            continue
        state, why = load_result(path)
        if state == "corrupt":
            print("%s: rebuilt from %s but still %s" % (path, name, why), file=sys.stderr)
        else:
            print("rebuilt %s from its %s blob (broken ELF headers)" % (os.path.basename(path), name))

    failed = []
    for path in libs:
        state, why = load_result(path)
        if state == "corrupt":
            print("FATAL: corrupt bundled library %s (%s)" % (path, why), file=sys.stderr)
            failed.append(path)
        elif state == "unresolved":
            print("note: %s needs something this chroot lacks: %s"
                  % (os.path.basename(path), why), file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
