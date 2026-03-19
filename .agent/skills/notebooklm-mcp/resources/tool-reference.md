# NotebookLM MCP Tool Quick Reference

All tools are prefixed with `mcp_notebooklm-mcp_` when called via MCP.

## Auth (2 tools)
| MCP Tool | Purpose |
|----------|---------|
| `refresh_auth` | Reload tokens from disk |
| `save_auth_tokens` | Manually save cookies (fallback) |

## Notebooks (5 tools)
| MCP Tool | Required Params |
|----------|-----------------|
| `notebook_list` | — |
| `notebook_get` | notebook_id |
| `notebook_describe` | notebook_id |
| `notebook_create` | title? |
| `notebook_rename` | notebook_id, new_title |
| `notebook_delete` | notebook_id, **confirm=True** |

## Sources (7 tools)
| MCP Tool | Required Params |
|----------|-----------------|
| `source_add` | notebook_id, source_type, + type-specific |
| `source_list_drive` | notebook_id |
| `source_sync_drive` | source_ids, **confirm=True** |
| `source_rename` | notebook_id, source_id, new_title |
| `source_delete` | source_id/source_ids, **confirm=True** |
| `source_describe` | source_id |
| `source_get_content` | source_id |

### source_add source_type values
| Type | Required | Optional |
|------|----------|----------|
| `url` | `url` or `urls` | `wait`, `wait_timeout` |
| `text` | `text` | `title`, `wait` |
| `file` | `file_path` | `wait` |
| `drive` | `document_id`, `doc_type` | `wait` |

## Research (3 tools)
| MCP Tool | Required Params |
|----------|-----------------|
| `research_start` | query | source?, mode?, notebook_id?, title? |
| `research_status` | notebook_id | task_id?, max_wait?, compact? |
| `research_import` | notebook_id, task_id | source_indices? |

## Query (3 tools)
| MCP Tool | Required Params |
|----------|-----------------|
| `notebook_query` | notebook_id, query |
| `cross_notebook_query` | query | notebook_names?, tags?, all? |
| `chat_configure` | notebook_id | goal?, custom_prompt?, response_length? |

## Studio (4 tools)
| MCP Tool | Required Params |
|----------|-----------------|
| `studio_create` | notebook_id, artifact_type, **confirm=True** |
| `studio_status` | notebook_id |
| `studio_delete` | notebook_id, artifact_id, **confirm=True** |
| `studio_revise` | notebook_id, artifact_id, slide_instructions, **confirm=True** |

## Download & Export (2 tools)
| MCP Tool | Required Params |
|----------|-----------------|
| `download_artifact` | notebook_id, artifact_type, output_path |
| `export_artifact` | notebook_id, artifact_id, export_type |

## Notes (1 tool, 4 actions)
| Action | Required Params |
|--------|-----------------|
| `list` | notebook_id |
| `create` | notebook_id, content |
| `update` | notebook_id, note_id, content |
| `delete` | notebook_id, note_id, **confirm=True** |

## Sharing (4 tools)
| MCP Tool | Required Params |
|----------|-----------------|
| `notebook_share_status` | notebook_id |
| `notebook_share_public` | notebook_id |
| `notebook_share_invite` | notebook_id, email |
| `notebook_share_batch` | notebook_id, recipients, **confirm=True** |

## Batch & Advanced (3 tools)
| MCP Tool | Required Params |
|----------|-----------------|
| `batch` | action | + action-specific |
| `pipeline` | action | notebook_id?, pipeline_name? |
| `tag` | action | notebook_id?, tags?, query? |

## Server (1 tool)
| MCP Tool | Purpose |
|----------|---------|
| `server_info` | Version check and update info |

## ⚠️ Tools Requiring confirm=True
- `notebook_delete`
- `source_delete`
- `source_sync_drive`
- `studio_create`
- `studio_delete`
- `studio_revise`
- `notebook_share_batch`
- `batch` (for delete action)
