-- Kernel Code Index - SQLite Schema
-- Stores symbols extracted from Linux kernel source via ctags

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    subsystem TEXT,          -- e.g. "drivers/gpio", "mm", "fs"
    line_count INTEGER
);

CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,      -- function, macro, struct, enum, variable, typedef, etc.
    file_id INTEGER NOT NULL,
    line INTEGER NOT NULL,
    pattern TEXT,            -- regex pattern from ctags (useful for context)
    typeref TEXT,            -- return type / type reference
    signature TEXT,          -- function parameters
    is_static INTEGER DEFAULT 0,  -- file-scoped (static)
    FOREIGN KEY (file_id) REFERENCES files(id)
);

CREATE TABLE IF NOT EXISTS call_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_id INTEGER NOT NULL,   -- symbol.id of the caller function
    callee_id INTEGER NOT NULL,   -- symbol.id of the callee function
    call_site_file_id INTEGER NOT NULL,
    call_site_line INTEGER NOT NULL,
    FOREIGN KEY (caller_id) REFERENCES symbols(id),
    FOREIGN KEY (callee_id) REFERENCES symbols(id),
    FOREIGN KEY (call_site_file_id) REFERENCES files(id)
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
CREATE INDEX IF NOT EXISTS idx_symbols_kind ON symbols(kind);
CREATE INDEX IF NOT EXISTS idx_symbols_file ON symbols(file_id);
CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
CREATE INDEX IF NOT EXISTS idx_files_subsystem ON files(subsystem);
CREATE INDEX IF NOT EXISTS idx_call_caller ON call_relations(caller_id);
CREATE INDEX IF NOT EXISTS idx_call_callee ON call_relations(callee_id);
