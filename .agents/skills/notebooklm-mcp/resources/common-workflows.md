# Common Workflows

## 1. Quick Knowledge Lookup

Goal: Ask a question against an existing notebook.

```
notebook_list()                              # find notebook
notebook_query(notebook_id, "your question") # ask
```

## 2. Research a Topic from Scratch

Goal: Search the web, import findings, generate a podcast.

```
notebook_create(title="Topic Research")
research_start(query="topic", notebook_id=id, source="web", mode="deep")
research_status(notebook_id=id, task_id=tid, max_wait=300)
research_import(notebook_id=id, task_id=tid)
studio_create(notebook_id=id, artifact_type="audio", audio_format="deep_dive", confirm=True)
studio_status(notebook_id=id)   # poll until completed
download_artifact(notebook_id=id, artifact_type="audio", output_path="podcast.mp3")
```

## 3. Build a Study Kit

Goal: From a PDF, generate a study guide + flashcards + quiz.

```
notebook_create(title="Study: Subject")
source_add(notebook_id=id, source_type="file", file_path="/path/file.pdf", wait=True)
studio_create(notebook_id=id, artifact_type="report", report_format="Study Guide", confirm=True)
studio_create(notebook_id=id, artifact_type="flashcards", difficulty="medium", confirm=True)
studio_create(notebook_id=id, artifact_type="quiz", question_count=10, confirm=True)
studio_status(notebook_id=id)   # check all are done
download_artifact(notebook_id=id, artifact_type="report", output_path="guide.md")
download_artifact(notebook_id=id, artifact_type="flashcards", output_path="cards.json")
download_artifact(notebook_id=id, artifact_type="quiz", output_path="quiz.html", output_format="html")
```

## 4. Aggregate Intelligence Across Notebooks

Goal: Query a question across multiple tagged notebooks.

```
tag(action="add", notebook_id=id1, tags="finance,research")
tag(action="add", notebook_id=id2, tags="finance,market")
cross_notebook_query(query="What are the key trends?", tags="finance")
```

## 5. Ingest Multiple URLs at Once

```
source_add(
    notebook_id=id,
    source_type="url",
    urls=["https://a.com", "https://b.com", "https://c.com"]
)
```

## 6. Create a Presentation from Sources

```
studio_create(
    notebook_id=id,
    artifact_type="slide_deck",
    slide_format="detailed_deck",
    focus_prompt="Focus on key findings and recommendations",
    confirm=True
)
studio_status(notebook_id=id)   # poll
# Optionally revise specific slides:
studio_revise(
    notebook_id=id,
    artifact_id=aid,
    slide_instructions=[
        {"slide": 1, "instruction": "Add a subtitle with the date"},
        {"slide": 3, "instruction": "Simplify the bullet points"}
    ],
    confirm=True
)
download_artifact(notebook_id=id, artifact_type="slide_deck", output_path="deck.pptx", slide_deck_format="pptx")
```

## 7. Share a Notebook

```
notebook_share_public(notebook_id=id, is_public=True)  # get public link
notebook_share_invite(notebook_id=id, email="user@example.com", role="editor")
notebook_share_batch(
    notebook_id=id,
    recipients=[
        {"email": "a@example.com", "role": "viewer"},
        {"email": "b@example.com", "role": "editor"}
    ],
    confirm=True
)
```

## 8. Pipeline: URL to Podcast (One-Step)

```
pipeline(action="list")   # see available pipelines
pipeline(action="run", notebook_id=id, pipeline_name="ingest-and-podcast", input_url="https://article.com")
```
