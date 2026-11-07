"""Read Windows memory/process counters without importing ML libraries."""
import ctypes as C
from ctypes import wintypes as W

kernel = C.WinDLL('kernel32', use_last_error=True)
psapi = C.WinDLL('psapi', use_last_error=True)

class Memory(C.Structure):
    _fields_ = [('length', W.DWORD), ('load', W.DWORD)] + [(key, C.c_ulonglong) for key in
        ('physical_total', 'physical_available', 'commit_limit', 'commit_available', 'virtual_total', 'virtual_available', 'extended')]

class Counters(C.Structure):
    _fields_ = [('cb', W.DWORD), ('faults', W.DWORD)] + [(key, C.c_size_t) for key in
        ('peak_working_set', 'working_set', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile', 'private')]

class Entry(C.Structure):
    _fields_ = [('size', W.DWORD), ('usage', W.DWORD), ('pid', W.DWORD), ('heap', C.c_size_t),
                ('module', W.DWORD), ('threads', W.DWORD), ('parent', W.DWORD), ('priority', W.LONG),
                ('flags', W.DWORD), ('name', W.WCHAR * 260)]

kernel.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
kernel.OpenProcess.restype = W.HANDLE
kernel.CloseHandle.argtypes = [W.HANDLE]
kernel.GlobalMemoryStatusEx.argtypes = [C.POINTER(Memory)]
psapi.GetProcessMemoryInfo.argtypes = [W.HANDLE, C.POINTER(Counters), W.DWORD]
kernel.CreateToolhelp32Snapshot.argtypes = [W.DWORD, W.DWORD]
kernel.CreateToolhelp32Snapshot.restype = W.HANDLE
kernel.Process32FirstW.argtypes = [W.HANDLE, C.POINTER(Entry)]
kernel.Process32NextW.argtypes = [W.HANDLE, C.POINTER(Entry)]

def system_memory():
    value = Memory()
    value.length = C.sizeof(value)
    if not kernel.GlobalMemoryStatusEx(C.byref(value)):
        raise C.WinError(C.get_last_error())
    return {name: getattr(value, name) for name in ('physical_total', 'physical_available', 'commit_limit', 'commit_available')}

def process_memory(pid):
    handle = kernel.OpenProcess(0x410, False, pid)
    if not handle:
        return None
    try:
        value = Counters()
        value.cb = C.sizeof(value)
        if not psapi.GetProcessMemoryInfo(handle, C.byref(value), value.cb):
            return None
        return {'working_set': value.working_set, 'private_bytes': value.private, 'peak_working_set': value.peak_working_set}
    finally:
        kernel.CloseHandle(handle)

def process_tree(root):
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == C.c_void_p(-1).value:
        raise C.WinError(C.get_last_error())
    parents = {}
    try:
        entry = Entry()
        entry.size = C.sizeof(entry)
        more = kernel.Process32FirstW(snapshot, C.byref(entry))
        while more:
            parents[entry.pid] = entry.parent
            more = kernel.Process32NextW(snapshot, C.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    children = {root}
    while True:
        expanded = children | {pid for pid, parent in parents.items() if parent in children}
        if expanded == children:
            return sorted(children)
        children = expanded

class Job:
    """Closing this job terminates only the assigned diagnostic process tree."""
    def __init__(self, process):
        class Basic(C.Structure):
            _fields_ = [('process_time', C.c_longlong), ('job_time', C.c_longlong), ('flags', W.DWORD),
                        ('min_ws', C.c_size_t), ('max_ws', C.c_size_t), ('active', W.DWORD),
                        ('affinity', C.c_size_t), ('priority', W.DWORD), ('scheduling', W.DWORD)]
        class IO(C.Structure):
            _fields_ = [(name, C.c_ulonglong) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
        class Extended(C.Structure):
            _fields_ = [('basic', Basic), ('io', IO)] + [(name, C.c_size_t) for name in
                ('process_memory', 'job_memory', 'peak_process_memory', 'peak_job_memory')]
        kernel.CreateJobObjectW.argtypes = [C.c_void_p, W.LPCWSTR]
        kernel.CreateJobObjectW.restype = W.HANDLE
        kernel.SetInformationJobObject.argtypes = [W.HANDLE, C.c_int, C.c_void_p, W.DWORD]
        kernel.AssignProcessToJobObject.argtypes = [W.HANDLE, W.HANDLE]
        self.handle = kernel.CreateJobObjectW(None, None)
        limits = Extended()
        limits.basic.flags = 0x2000
        if (not self.handle or not kernel.SetInformationJobObject(self.handle, 9, C.byref(limits), C.sizeof(limits))
                or not kernel.AssignProcessToJobObject(self.handle, W.HANDLE(int(process._handle)))):
            error = C.WinError(C.get_last_error())
            self.close()
            if process.poll() is None:
                process.kill()
            raise error

    def close(self):
        if self.handle:
            kernel.CloseHandle(self.handle)
            self.handle = None
