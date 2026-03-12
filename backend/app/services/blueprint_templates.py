"""Pre-built blueprint templates that showcase the Blueprint system."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

BLUEPRINT_TEMPLATES = [
    {
        "name": "Document Analyzer",
        "description": "Extracts structured data from a document — entities, dates, amounts — and validates the output.",
        "is_template": True,
        "nodes": [
            {
                "id": "fetch_doc",
                "type": "fetch_document",
                "label": "Load Document",
                "config": {},
                "dependencies": [],
                "position": {"x": 100, "y": 200},
            },
            {
                "id": "split",
                "type": "text_splitter",
                "label": "Split into Chunks",
                "config": {"chunk_size": 2000, "overlap": 200},
                "dependencies": ["fetch_doc"],
                "position": {"x": 350, "y": 200},
            },
            {
                "id": "extract",
                "type": "llm_extract",
                "label": "Extract Entities",
                "config": {
                    "extraction_schema": {
                        "required": ["entities", "dates", "amounts"],
                    },
                },
                "dependencies": ["split"],
                "position": {"x": 600, "y": 200},
            },
            {
                "id": "validate",
                "type": "json_validator",
                "label": "Validate JSON",
                "config": {
                    "schema": {"required": ["entities"]},
                },
                "dependencies": ["extract"],
                "position": {"x": 850, "y": 200},
            },
            {
                "id": "format",
                "type": "output_formatter",
                "label": "Format Output",
                "config": {"format": "json"},
                "dependencies": ["validate"],
                "position": {"x": 1100, "y": 200},
            },
        ],
        "context_config": {"accepted_types": ["pdf", "docx", "txt"]},
        "tool_scope": ["data_extractor"],
        "retry_policy": {"max_retries": 2},
        "output_schema": {"type": "json"},
    },
    {
        "name": "Research Report",
        "description": "Fetches multiple sources, summarizes each, then synthesizes into a cohesive research report.",
        "is_template": True,
        "nodes": [
            {
                "id": "source_1",
                "type": "fetch_url",
                "label": "Source 1",
                "config": {"url": ""},
                "dependencies": [],
                "position": {"x": 100, "y": 100},
            },
            {
                "id": "source_2",
                "type": "fetch_url",
                "label": "Source 2",
                "config": {"url": ""},
                "dependencies": [],
                "position": {"x": 100, "y": 250},
            },
            {
                "id": "source_3",
                "type": "fetch_url",
                "label": "Source 3",
                "config": {"url": ""},
                "dependencies": [],
                "position": {"x": 100, "y": 400},
            },
            {
                "id": "split",
                "type": "text_splitter",
                "label": "Combine & Split",
                "config": {"chunk_size": 3000, "overlap": 300},
                "dependencies": ["source_1", "source_2", "source_3"],
                "position": {"x": 400, "y": 250},
            },
            {
                "id": "summarize",
                "type": "llm_summarize",
                "label": "Summarize Sources",
                "config": {"max_length": "medium"},
                "dependencies": ["split"],
                "position": {"x": 700, "y": 250},
            },
            {
                "id": "synthesize",
                "type": "llm_generate",
                "label": "Synthesize Report",
                "config": {
                    "system_prompt": (
                        "You are a research analyst. Given summaries of multiple sources, "
                        "write a cohesive research report with: executive summary, key findings, "
                        "analysis, and recommendations."
                    ),
                },
                "dependencies": ["summarize"],
                "position": {"x": 1000, "y": 250},
            },
            {
                "id": "format",
                "type": "output_formatter",
                "label": "Format as Markdown",
                "config": {"format": "markdown"},
                "dependencies": ["synthesize"],
                "position": {"x": 1300, "y": 250},
            },
        ],
        "context_config": {"max_context_tokens": 12000},
        "tool_scope": ["web_search", "summarizer"],
        "retry_policy": {"max_retries": 2},
        "output_schema": {"type": "markdown"},
    },
    {
        "name": "Code Review",
        "description": "Injects code with a style guide, runs an LLM review with severity ratings, and validates the output.",
        "is_template": True,
        "nodes": [
            {
                "id": "template",
                "type": "template_renderer",
                "label": "Inject Code + Style Guide",
                "config": {
                    "template": (
                        "## Code to Review\n\n```\n{{text}}\n```\n\n"
                        "## Style Guide\n- Follow PEP 8\n- Use type hints\n"
                        "- Handle errors explicitly\n- No unused imports"
                    ),
                },
                "dependencies": [],
                "position": {"x": 100, "y": 200},
            },
            {
                "id": "review",
                "type": "llm_review",
                "label": "Review Code",
                "config": {"review_type": "code"},
                "dependencies": ["template"],
                "position": {"x": 400, "y": 200},
            },
            {
                "id": "validate",
                "type": "json_validator",
                "label": "Validate Feedback",
                "config": {"schema": {}},
                "dependencies": ["review"],
                "position": {"x": 700, "y": 200},
            },
            {
                "id": "format",
                "type": "output_formatter",
                "label": "Format Report",
                "config": {"format": "json"},
                "dependencies": ["validate"],
                "position": {"x": 1000, "y": 200},
            },
        ],
        "context_config": {},
        "tool_scope": ["code_executor"],
        "retry_policy": {"max_retries": 2},
        "output_schema": {"type": "json"},
    },
    {
        "name": "Data Extraction Pipeline",
        "description": "Reads a document, splits it, extracts structured data, validates, and formats the output.",
        "is_template": True,
        "nodes": [
            {
                "id": "fetch_doc",
                "type": "fetch_document",
                "label": "Load Document",
                "config": {},
                "dependencies": [],
                "position": {"x": 100, "y": 200},
            },
            {
                "id": "split",
                "type": "text_splitter",
                "label": "Split Text",
                "config": {"chunk_size": 2000, "overlap": 200},
                "dependencies": ["fetch_doc"],
                "position": {"x": 350, "y": 200},
            },
            {
                "id": "extract",
                "type": "llm_extract",
                "label": "Extract to Schema",
                "config": {
                    "extraction_schema": {
                        "required": ["entities", "key_facts"],
                    },
                },
                "dependencies": ["split"],
                "position": {"x": 600, "y": 200},
            },
            {
                "id": "validate",
                "type": "json_validator",
                "label": "Validate Output",
                "config": {
                    "schema": {"required": ["entities"]},
                },
                "dependencies": ["extract"],
                "position": {"x": 850, "y": 200},
            },
            {
                "id": "format",
                "type": "output_formatter",
                "label": "Format JSON",
                "config": {"format": "json"},
                "dependencies": ["validate"],
                "position": {"x": 1100, "y": 200},
            },
        ],
        "context_config": {"accepted_types": ["pdf", "docx", "txt"]},
        "tool_scope": ["data_extractor", "document_reader"],
        "retry_policy": {"max_retries": 2},
        "output_schema": {"type": "json"},
    },
    {
        "name": "Content Generator",
        "description": "Generates content from a topic template, checks for issues with a linter, then refines.",
        "is_template": True,
        "nodes": [
            {
                "id": "template",
                "type": "template_renderer",
                "label": "Set Topic & Tone",
                "config": {
                    "template": (
                        "Topic: {{text}}\n\n"
                        "Write a well-structured article about this topic. "
                        "Use a professional but accessible tone. "
                        "Include an introduction, 3-4 key sections, and a conclusion."
                    ),
                },
                "dependencies": [],
                "position": {"x": 100, "y": 200},
            },
            {
                "id": "generate",
                "type": "llm_generate",
                "label": "Generate Content",
                "config": {
                    "system_prompt": "You are an expert content writer. Write high-quality articles.",
                },
                "dependencies": ["template"],
                "position": {"x": 400, "y": 200},
            },
            {
                "id": "lint",
                "type": "run_linter",
                "label": "Check Style",
                "config": {"language": "text"},
                "dependencies": ["generate"],
                "position": {"x": 700, "y": 200},
            },
            {
                "id": "refine",
                "type": "llm_generate",
                "label": "Refine & Polish",
                "config": {
                    "system_prompt": (
                        "Review and improve the following article. Fix any grammar issues, "
                        "improve clarity, and ensure good flow between sections."
                    ),
                },
                "dependencies": ["lint"],
                "position": {"x": 1000, "y": 200},
            },
            {
                "id": "format",
                "type": "output_formatter",
                "label": "Final Format",
                "config": {"format": "markdown"},
                "dependencies": ["refine"],
                "position": {"x": 1300, "y": 200},
            },
        ],
        "context_config": {},
        "tool_scope": [],
        "retry_policy": {"max_retries": 1},
        "output_schema": {"type": "markdown"},
    },
]


async def seed_blueprint_templates(supabase_client) -> None:
    """Seed pre-built blueprint templates if they don't already exist."""
    for template in BLUEPRINT_TEMPLATES:
        try:
            existing = (
                supabase_client.table("blueprints")
                .select("id")
                .eq("name", template["name"])
                .eq("is_template", True)
                .execute()
            )
            if existing.data:
                continue

            supabase_client.table("blueprints").insert({
                **template,
                "user_id": "00000000-0000-0000-0000-000000000000",  # System user for templates
            }).execute()
            logger.info("Seeded blueprint template: %s", template["name"])
        except Exception:
            logger.warning("Failed to seed blueprint template: %s", template["name"], exc_info=True)
