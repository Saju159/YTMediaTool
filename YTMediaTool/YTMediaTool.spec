# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['BasicPage', 'SMLDpage', 'SettingsPage', 'AboutPage', 'SMLD', 'Commmon', 'CommonGui', 'Info', 'Settings', 'SMLDprogressTracker', 'Version', 'YtdlpManager', '_suggestions', 'dataclasses', 'warnings', '_contextvars', '_pyio', 'ctypes', 'pdb', 'tarfile', 'cmath', 'mimetypes', '_asyncio', '_codecs', 'enum', 'xml', 'io', '_frozen_importlib_external', 'mmap', 'functools', 'gettext', '_wmi', 'cProfile', 'sysconfig', 'select', 'turtledemo', 'html', 'weakref', '_strptime', 'wsgiref', '_string', 'token', '_frozen_importlib', 'quopri', 'marshal', '_heapq', 'difflib', 'syslog', 'dis', 'tracemalloc', 'sys', 'pyclbr', '_symtable', '_codecs_iso2022', 'pydoc_data', 'heapq', '_ctypes', '_codecs_cn', '_lzma', 'ensurepip', 'getpass', 'ast', '_multiprocessing', '_interpchannels', 'winsound', 'zipapp', 'compileall', 'typing', 'queue', 'tomllib', 'pydoc', '_scproxy', 'pickletools', 'signal', 'unicodedata', '_opcode_metadata', 'copyreg', 'uuid', '_winapi', 'gzip', 'subprocess', 'filecmp', 'graphlib', 'profile', '_interpqueues', 'bisect', '_curses', '_sha1', 'colorsys', '_locale', '_apple_support', 'hmac', 'code', '_md5', 'gc', 'runpy', 'sched', 'socketserver', 'turtle', '_warnings', 'pickle', 'pyexpat', 'zipfile', 'ipaddress', '_codecs_kr', 'msvcrt', 'pprint', '_blake2', 'sre_parse', '_imp', '_compat_pickle', '_threading_local', '_pickle', '_statistics', 'netrc', 'concurrent', '_stat', 'fileinput', '_sha2', 'faulthandler', '_osx_support', 'timeit', 'termios', 'this', 'fractions', 'pstats', 'symtable', '_zoneinfo', '_functools', '_codecs_tw', 'py_compile', 'threading', '_sqlite3', 'pathlib', '_pydatetime', 'fnmatch', '_tkinter', 'pkgutil', 'contextlib', 'copy', '_signal', '_ssl', '_bz2', '_tokenize', 'base64', 'codeop', 'datetime', 'decimal', 'logging', '_collections_abc', 'cmd', 'os', 'time', 'getopt', '_csv', 'tempfile', 'readline', 'curses', 'smtplib', '_sre', 'shutil', 'hashlib', '_lsprof', 'imaplib', 'mailbox', 'errno', 'urllib', 'asyncio', 'webbrowser', '_curses_panel', 'multiprocessing', '_py_abc', 'numbers', 're', '_pylong', 'sqlite3', 'shelve', 'http', 'zlib', 'contextvars', 'bdb', 'nturl2path', 'itertools', 'plistlib', 'textwrap', 'socket', '_io', '_markupbase', '_aix_support', '_bisect', '_socket', 'tty', '_posixsubprocess', '_weakref', '_overlapped', 'traceback', 'locale', '_codecs_hk', 'trace', '_colorize', '_typing', 'optparse', '_decimal', '__future__', 'platform', 'stat', 'xmlrpc', 'wave', 'bz2', '_queue', '_interpreters', 'modulefinder', 'nt', 'codecs', 'sre_compile', '_pyrepl', '_abc', 'builtins', 'lzma', 'atexit', 'configparser', '_multibytecodec', '_codecs_jp', 'dbm', 'csv', 'doctest', 'email', 'operator', 'posix', 'ssl', 'unittest', 'tokenize', 'ntpath', '_json', 'antigravity', 'glob', 'inspect', 'site', 'winreg', 'tkinter', '_thread', 'abc', 'selectors', 'zoneinfo', 'types', '_compression', '_datetime', '_android_support', '_random', 'fcntl', 'math', 'shlex', 'pwd', 'opcode', '_struct', 'poplib', '_dbm', 'string', '_weakrefset', 'array', 'struct', 'importlib', '_hashlib', 'genericpath', 'pty', 'venv', 'sre_constants', '_gdbm', '_sha3', 'secrets', 'grp', '_elementtree', '_tracemalloc', 'collections', 'tabnanny', 'encodings', '_sitebuiltins', 'calendar', 'zipimport', 'ftplib', '_posixshmem', '_collections', 'posixpath', 'linecache', 'resource', 'binascii', 'stringprep', '_ios_support', 'json', '_operator', 'argparse', '_opcode', '_pydecimal', '_uuid', 'random', 'rlcompleter', 'statistics', 'idlelib', 'keyword', '_sysconfig', '_ast', 'reprlib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YTMediaTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YTMediaTool',
)
