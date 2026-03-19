---
name: managing-notebooklm
description: "Manages Google NotebookLM notebooks, sources, research, and studio artifacts via MCP. Use when user mentions NotebookLM, notebooks, research, podcasts, study guides, quizzes, flashcards, mind maps, or wants to query knowledge bases."
---
# Managing NotebookLM via MCP

## When to use this skill

- User wants to create, list, query, or manage NotebookLM notebooks
- User wants to add sources (URLs, files, text, Drive docs) to a notebook
- User wants to run research (web or Drive) and import findings
- User wants to generate studio artifacts (audio, video, slides, reports, quizzes, etc.)
- User wants to query existing notebook knowledge or cross-query multiple notebooks
- User asks about NotebookLM content, sharing, notes, or exports

## Key Concepts

- **Notebook**: A collection of sources. Identified by UUID.
- **Source**: Content added to a notebook (URL, file, text, Drive doc). Identified by UUID.
- **Artifact**: Generated content from Studio (audio, video, report, etc.). Identified by UUID.
- **Note**: User-created notes within a notebook.
- **Tag**: Labels for organizing and selecting notebooks.

## Authentication

If any tool returns an auth error:

1. Run `nlm login` in terminal (opens browser for Google sign-in)
2. Call `refresh_auth` to reload tokens
3. Only use `save_auth_tokens` as a last-resort fallback

Check auth: `nlm login --check`

## Workflow Patterns

### Pattern 1: Discover → Query

```
[ ] List notebooks → notebook_list
[ ] Get notebook details → notebook_get(notebook_id)
[ ] Ask questions → notebook_query(notebook_id, query)
```

### Pattern 2: Research → Ingest → Generate

```
[ ] Start research → research_start(query, source="web", mode="fast|deep")
[ ] Poll status → research_status(notebook_id, task_id)
[ ] Import sources → research_import(notebook_id, task_id)
[ ] Generate artifact → studio_create(notebook_id, artifact_type, confirm=True)
[ ] Check status → studio_status(notebook_id)
[ ] Download → download_artifact(notebook_id, artifact_type, output_path)
```

### Pattern 3: Build Notebook from Local Content

```
[ ] Create notebook → notebook_create(title)
[ ] Add sources → source_add(notebook_id, source_type, ...)
[ ] Wait for processing (use wait=True)
[ ] Query or generate artifacts
```

### Pattern 4: Cross-Notebook Intelligence

```
[ ] Tag notebooks → tag(action="add", notebook_id, tags)
[ ] Query across → cross_notebook_query(query, tags="...")
```

## Tool Reference by Category

### Notebooks

| Action      | Tool                  | Key Args                          |
| ----------- | --------------------- | --------------------------------- |
| List all    | `notebook_list`     | `max_results`                   |
| Details     | `notebook_get`      | `notebook_id`                   |
| AI summary  | `notebook_describe` | `notebook_id`                   |
| Create      | `notebook_create`   | `title`                         |
| Rename      | `notebook_rename`   | `notebook_id`, `new_title`    |
| Delete ⚠️ | `notebook_delete`   | `notebook_id`, `confirm=True` |

### Sources

| Action       | Tool                   | Key Args                                                                |
| ------------ | ---------------------- | ----------------------------------------------------------------------- |
| Add URL      | `source_add`         | `notebook_id`, `source_type="url"`, `url`                         |
| Add file     | `source_add`         | `notebook_id`, `source_type="file"`, `file_path`                  |
| Add text     | `source_add`         | `notebook_id`, `source_type="text"`, `text`, `title`            |
| Add Drive    | `source_add`         | `notebook_id`, `source_type="drive"`, `document_id`, `doc_type` |
| Bulk URLs    | `source_add`         | `notebook_id`, `source_type="url"`, `urls=[...]`                  |
| List (Drive) | `source_list_drive`  | `notebook_id`                                                         |
| Sync Drive   | `source_sync_drive`  | `source_ids`, `confirm=True`                                        |
| AI summary   | `source_describe`    | `source_id`                                                           |
| Raw content  | `source_get_content` | `source_id`                                                           |
| Rename       | `source_rename`      | `notebook_id`, `source_id`, `new_title`                           |
| Delete ⚠️  | `source_delete`      | `source_id` or `source_ids`, `confirm=True`                       |

### Research

| Action | Tool                | Key Args                                                |
| ------ | ------------------- | ------------------------------------------------------- |
| Start  | `research_start`  | `query`, `source="web\|drive"`, `mode="fast\|deep"` |
| Poll   | `research_status` | `notebook_id`, `task_id`, `max_wait`              |
| Import | `research_import` | `notebook_id`, `task_id`, `source_indices`        |

> **Deep research** takes ~5 min, finds ~40 sources (web only).
> **Fast research** takes ~30s, finds ~10 sources.

### Querying

| Action         | Tool                     | Key Args                                                          |
| -------------- | ------------------------ | ----------------------------------------------------------------- |
| Query notebook | `notebook_query`       | `notebook_id`, `query`, `source_ids`, `conversation_id`   |
| Cross-query    | `cross_notebook_query` | `query`, `notebook_names\|tags\|all`                            |
| Configure chat | `chat_configure`       | `notebook_id`, `goal`, `custom_prompt`, `response_length` |

- Use `conversation_id` from previous response for follow-up questions
- `notebook_query` only searches EXISTING sources; use `research_start` for new

### Studio Artifacts

| Action        | Tool                  | Key Args                                                                   |
| ------------- | --------------------- | -------------------------------------------------------------------------- |
| Create        | `studio_create`     | `notebook_id`, `artifact_type`, `confirm=True`                       |
| Status        | `studio_status`     | `notebook_id`                                                            |
| Delete ⚠️   | `studio_delete`     | `notebook_id`, `artifact_id`, `confirm=True`                         |
| Revise slides | `studio_revise`     | `notebook_id`, `artifact_id`, `slide_instructions`, `confirm=True` |
| Download      | `download_artifact` | `notebook_id`, `artifact_type`, `output_path`                        |
| Export        | `export_artifact`   | `notebook_id`, `artifact_id`, `export_type="docs\|sheets"`            |

**Artifact types and their options:**

- **audio**: `audio_format` (deep_dive|brief|critique|debate), `audio_length` (short|default|long)
- **video**: `video_format` (explainer|brief|cinematic), `visual_style` (auto_select|classic|whiteboard|kawaii|anime|watercolor|retro_print|heritage|paper_craft)
- **infographic**: `orientation` (landscape|portrait|square), `detail_level` (concise|standard|detailed), `infographic_style` (auto_select|sketch_note|professional|bento_grid|editorial|instructional|bricks|clay|anime|kawaii|scientific)
- **slide_deck**: `slide_format` (detailed_deck|presenter_slides), `slide_length` (short|default)
- **report**: `report_format` (Briefing Doc|Study Guide|Blog Post|Create Your Own), `custom_prompt`
- **flashcards**: `difficulty` (easy|medium|hard)
- **quiz**: `question_count`, `difficulty` (easy|medium|hard)
- **data_table**: `description` (required)
- **mind_map**: `title`

Common: `language` (BCP-47), `focus_prompt`, `source_ids`

### Notes

| Action      | Tool     | Key Args                                                            |
| ----------- | -------- | ------------------------------------------------------------------- |
| List        | `note` | `notebook_id`, `action="list"`                                  |
| Create      | `note` | `notebook_id`, `action="create"`, `content`, `title`        |
| Update      | `note` | `notebook_id`, `action="update"`, `note_id`, `content`      |
| Delete ⚠️ | `note` | `notebook_id`, `action="delete"`, `note_id`, `confirm=True` |

### Sharing

| Action       | Tool                      | Key Args                                                |
| ------------ | ------------------------- | ------------------------------------------------------- |
| Status       | `notebook_share_status` | `notebook_id`                                         |
| Public link  | `notebook_share_public` | `notebook_id`, `is_public`                          |
| Invite one   | `notebook_share_invite` | `notebook_id`, `email`, `role`                    |
| Invite batch | `notebook_share_batch`  | `notebook_id`, `recipients=[...]`, `confirm=True` |

### Batch & Advanced

| Action      | Tool            | Key Args                                                  |
| ----------- | --------------- | --------------------------------------------------------- |
| Batch ops   | `batch`       | `action`, `notebook_names\|tags\|all`                   |
| Pipelines   | `pipeline`    | `action="run\|list"`, `notebook_id`, `pipeline_name` |
| Tags        | `tag`         | `action="add\|remove\|list\|select"`                       |
| Server info | `server_info` | *(none)*                                                |

## Critical Rules

1. **Always confirm destructive ops**: `notebook_delete`, `source_delete`, `studio_delete`, `source_sync_drive`, and `notebook_share_batch` all require `confirm=True`. Ask the user before confirming.
2. **notebook_query ≠ research_start**: `notebook_query` only searches existing sources. To find NEW sources, use `research_start`.
3. **Research is async**: Always follow `research_start` → `research_status` → `research_import`.
4. **Studio is async**: After `studio_create`, poll `studio_status` until completed.
5. **Use `wait=True`** on `source_add` when you need to query the source immediately after adding it.
6. **source_get_content** is much faster than `notebook_query` for raw text extraction.
7. WARNING: **Only use `source_get_content` for short text snippets.** For long documents or complex PDFs, ALWAYS default to `notebook_query` or `source_describe` to extract specific information without blowing up the context window.
8. **Slide revision** creates a NEW artifact; the original is preserved.
9. **Rate limits**: Use `cross_notebook_query(all=True)` with caution.

## Resources

- [Common Workflows](resources/common-workflows.md)
- [Tool Quick Reference](resources/tool-reference.md)
