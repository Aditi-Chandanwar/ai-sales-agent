# lead_registry package
#
# Persistent master database of every lead the system has ever
# discovered, keyed by company website domain, so history isn't lost
# between pipeline runs the way isolated CSV checkpoints would lose it.
#
# Storage is pluggable (see storage.py) - this package uses CSV today
# but is structured so a SQLite-backed storage class can be swapped in
# later with minimal changes elsewhere in the codebase.
