"""
Enhanced utility functions - exports for backward compatibility
"""
# Re-export core functions for backward compatibility
from wannabegit.core import (
    VCS_DIR,
    COMMITS_DIR,
    INDEX_FILE,
    HEAD_FILE,
    REFS_DIR,
    CONFIG_FILE,
    OBJECTS_DIR,
    Repository,
    RepositoryError,
    ensure_vcs_exists,
    read_json,
    write_json,
    generate_commit_id,
    hash_file_content,
    compress_content,
    decompress_content,
    get_file_hash,
    write_head,
    get_relative_path,
    format_timestamp,
    parse_timestamp
)

__all__ = [
    'VCS_DIR',
    'COMMITS_DIR',
    'INDEX_FILE',
    'HEAD_FILE',
    'REFS_DIR',
    'CONFIG_FILE',
    'OBJECTS_DIR',
    'Repository',
    'RepositoryError',
    'ensure_vcs_exists',
    'read_json',
    'write_json',
    'generate_commit_id',
    'hash_file_content',
    'compress_content',
    'decompress_content',
    'get_file_hash',
    'write_head',
    'get_relative_path',
    'format_timestamp',
    'parse_timestamp'
]