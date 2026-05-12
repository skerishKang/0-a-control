# server_handlers package — no imports from scripts.server at package level
# to avoid circular dependency. Each handler module resolves imports lazily.