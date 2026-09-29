"""Build the RTB evaluation deck: py -m pip install python-pptx; py docs/build_presentation.py"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

OUTPUT = Path(__file__).with_name("RTB_Databricks_CICD_GenAI.pptx")

NAVY = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x2E, 0x75, 0xB6)
TEAL = RGBColor(0x00, 0x89, 0x7B)
ORANGE = RGBColor(0xFF, 0x36, 0x21)
AMBER = RGBColor(0xF5, 0x9E, 0x0B)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
PURPLE = RGBColor(0x6A, 0x1B, 0x9A)
GREY = RGBColor(0x60, 0x60, 0x60)
LIGHT = RGBColor(0xF2, 0xF5, 0xFA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x22, 0x22, 0x22)
BRONZE = RGBColor(0xA0, 0x52, 0x2D)
SILVER = RGBColor(0x75, 0x75, 0x75)
GOLD = RGBColor(0xC9, 0x9A, 0x00)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def _style(paragraph, size, bold=False, color=DARK, align=None):
    paragraph.font.size = Pt(size)
    paragraph.font.bold = bold
    paragraph.font.color.rgb = color
    paragraph.font.name = "Segoe UI"
    if align is not None:
        paragraph.alignment = align


def new_slide(title, subtitle=None, notes=None):
    slide = prs.slides.add_slide(BLANK)
    band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.0))
    band.fill.solid()
    band.fill.fore_color.rgb = NAVY
    band.line.fill.background()
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.0), prs.slide_width, Inches(0.06))
    accent.fill.solid()
    accent.fill.fore_color.rgb = ORANGE
    accent.line.fill.background()
    text(slide, 0.5, 0.12, 12.3, 0.55, title, 28, bold=True, color=WHITE)
    if subtitle:
        text(slide, 0.5, 0.6, 12.3, 0.35, subtitle, 14, color=RGBColor(0xD0, 0xDC, 0xF0))
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide


def text(slide, x, y, w, h, content, size=16, bold=False, color=DARK, align=None):
    frame = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    frame.word_wrap = True
    for i, line in enumerate(content.split("\n")):
        paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        paragraph.text = line
        _style(paragraph, size, bold, color, align)
    return frame


def bullets(slide, x, y, w, h, items, size=16, color=DARK):
    """items: strings; prefix with '-' for a sub-bullet."""
    frame = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    frame.word_wrap = True
    for i, item in enumerate(items):
        paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        sub = item.startswith("-")
        paragraph.text = ("      - " + item[1:].strip()) if sub else ("\u2022  " + item)
        _style(paragraph, size - 2 if sub else size, color=GREY if sub else color)
        paragraph.space_after = Pt(6)
    return frame


def box(slide, x, y, w, h, content, fill=BLUE, size=14, bold=True, color=WHITE, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = fill
    shp.shadow.inherit = False
    frame = shp.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(frame, side, Inches(0.06))
    for i, line in enumerate(content.split("\n")):
        paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        paragraph.text = line
        _style(paragraph, size if i == 0 else size - 3, bold if i == 0 else False, color, PP_ALIGN.CENTER)
    return shp


def panel(slide, x, y, w, h, title, fill=LIGHT, border=BLUE):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.adjustments[0] = 0.05
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = border
    shp.line.width = Pt(1.5)
    shp.shadow.inherit = False
    text(slide, x + 0.1, y + 0.05, w - 0.2, 0.4, title, 14, bold=True, color=border)


def arrow(slide, x, y, w=0.4, h=0.35, direction="right", fill=GREY):
    kind = {"right": MSO_SHAPE.RIGHT_ARROW, "down": MSO_SHAPE.DOWN_ARROW, "up": MSO_SHAPE.UP_ARROW}[direction]
    shp = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    shp.shadow.inherit = False


def flow(slide, steps, y, h=1.1, x0=0.5, width=12.33, gap=0.45, size=14):
    """Horizontal chain of boxes joined by arrows. steps: [(text, colour), ...]."""
    w = (width - gap * (len(steps) - 1)) / len(steps)
    for i, (label, fill) in enumerate(steps):
        x = x0 + i * (w + gap)
        box(slide, x, y, w, h, label, fill, size)
        if i < len(steps) - 1:
            arrow(slide, x + w + 0.05, y + h / 2 - 0.17, gap - 0.1, 0.34)


def table(slide, x, y, w, rows, col_widths, size=13, header_fill=NAVY):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(0.4 * len(rows)))
    tbl = shape.table
    for c, width in enumerate(col_widths):
        tbl.columns[c].width = Inches(width)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = value
            cell.fill.solid()
            cell.fill.fore_color.rgb = header_fill if r == 0 else (LIGHT if r % 2 else WHITE)
            for paragraph in cell.text_frame.paragraphs:
                _style(paragraph, size, bold=(r == 0), color=WHITE if r == 0 else DARK)
    return tbl


# 1. Title ---------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.55), Inches(3), Inches(0.08))
bar.fill.solid()
bar.fill.fore_color.rgb = ORANGE
bar.line.fill.background()
text(slide, 0.8, 1.6, 11.5, 1.2, "CI/CD for Databricks with GenAI", 44, bold=True, color=WHITE)
text(slide, 0.8, 2.6, 11.5, 0.8, "GitHub Actions  |  Databricks Asset Bundles  |  QA -> PROD  |  AI-assisted DevOps",
     20, color=RGBColor(0xD0, 0xDC, 0xF0))
text(slide, 0.8, 3.9, 11.5, 1.5, "RTB C16 Case Study - Evaluation\nSales ETL pipeline: Bronze -> Silver -> Gold",
     18, color=WHITE)
slide.notes_slide.notes_text_frame.text = (
    "Introduce the project: an automated pipeline that tests, deploys and runs a Databricks ETL job, "
    "with AI generating reports so humans spend less time reading logs."
)

# 2. Business need -------------------------------------------------------------
slide = new_slide("Business Need", "Why do we need this pipeline?",
                  "Explain the pain points of manual deployment and how automation plus AI solves each one.")
panel(slide, 0.5, 1.4, 6.0, 5.6, "Problem today (manual process)", border=ORANGE)
bullets(slide, 0.7, 1.95, 5.7, 5.0, [
    "Notebooks copied to Databricks by hand",
    "No automatic testing -> bugs reach PROD",
    "No review / approval before PROD changes",
    "Engineers spend time reading long logs",
    "Release notes and docs written manually",
    "Secrets (tokens) sometimes shared in code",
], 17)
panel(slide, 6.83, 1.4, 6.0, 5.6, "Solution (this project)", border=GREEN)
bullets(slide, 7.03, 1.95, 5.7, 5.0, [
    "One push -> automatic test, deploy and run",
    "Lint, security scan and unit tests on every PR",
    "QA first, PROD only after manual approval",
    "AI summarises logs and finds root cause",
    "AI writes release notes, docs, workflow review",
    "Secrets stored in GitHub Secrets and redacted before AI",
], 17)

# 3. Tech stack ----------------------------------------------------------------
slide = new_slide("Tools and Technologies", "Simple, free and standard tools",
                  "Each tool has one clear job. Everything used here is free for this demo.")
tools = [
    ("GitHub", "Code, branches,\npull requests", NAVY),
    ("GitHub Actions", "CI/CD automation\n(workflows, runners)", BLUE),
    ("Databricks", "Free Edition,\nserverless + Unity Catalog", ORANGE),
    ("Asset Bundles", "databricks.yml -\ninfrastructure as code", PURPLE),
    ("PySpark + pytest", "ETL logic and\nunit tests", TEAL),
    ("flake8 / yamllint / bandit", "Code style, YAML check,\nsecurity scan", GREY),
    ("Google Gemini API", "GenAI reports\n(no VPN needed)", GREEN),
    ("Slack / Teams", "Pipeline result\nnotification", AMBER),
]
for i, (name, desc, colour) in enumerate(tools):
    col, row = i % 4, i // 4
    box(slide, 0.5 + col * 3.15, 1.5 + row * 2.8, 2.9, 2.4, f"{name}\n{desc}", colour, 18)

# 4. Architecture --------------------------------------------------------------
slide = new_slide("Solution Architecture", "How all the parts connect",
                  "Walk left to right: developer pushes code, GitHub Actions tests it, deploys to QA, then PROD "
                  "after approval. Logs flow to the AI which writes reports. Notification goes to the team.")
box(slide, 0.3, 2.3, 1.7, 1.4, "Developer\nfeature/* branch", GREY, 15)
arrow(slide, 2.05, 2.83)
box(slide, 2.5, 2.3, 1.8, 1.4, "GitHub Repo\nPull Request\nto main", NAVY, 15)
arrow(slide, 4.35, 2.83)
panel(slide, 4.8, 1.35, 3.0, 3.3, "CI (GitHub runner)", border=BLUE)
for i, step in enumerate(["Lint: flake8, yamllint", "Security: bandit", "Unit tests: pytest", "Bundle validate"]):
    box(slide, 4.95, 1.85 + i * 0.68, 2.7, 0.55, step, BLUE, 13)
arrow(slide, 7.85, 2.83)
panel(slide, 8.3, 1.35, 2.35, 3.3, "CD (deploy)", border=PURPLE)
box(slide, 8.45, 1.85, 2.05, 0.75, "Deploy + run\nQA", PURPLE, 14)
box(slide, 8.45, 2.75, 2.05, 0.6, "Manual approval", AMBER, 13)
box(slide, 8.45, 3.5, 2.05, 0.75, "Deploy + run\nPROD", PURPLE, 14)
arrow(slide, 10.7, 2.83)
panel(slide, 11.15, 1.35, 1.95, 3.3, "Databricks", border=ORANGE)
box(slide, 11.25, 1.9, 1.75, 1.1, "qa_catalog\nsales schema", ORANGE, 13)
box(slide, 11.25, 3.2, 1.75, 1.1, "prod_catalog\nsales schema", ORANGE, 13)
arrow(slide, 6.1, 4.75, 0.35, 0.5, "down")
arrow(slide, 9.3, 4.75, 0.35, 0.5, "down")
box(slide, 4.8, 5.35, 5.85, 1.0,
    "GenAI assistant (Gemini API)\nlogs in -> summary, release notes, docs, workflow review", GREEN, 16)
arrow(slide, 10.7, 5.68)
box(slide, 11.15, 5.35, 1.95, 1.0, "Reports +\nSlack / Teams", AMBER, 14)
box(slide, 0.3, 5.35, 4.0, 1.0, "GitHub Secrets\nDATABRICKS_TOKEN, GEMINI_API_KEY", GREY, 14)

# 5. End-to-end flow -----------------------------------------------------------
slide = new_slide("End-to-End Flow", "From code change to production in 8 simple steps",
                  "This is the full journey of one code change. Steps 1-4 are CI, 5-7 are CD, 8 is reporting.")
row1 = [("1. Code\nchange on\nfeature branch", GREY), ("2. Open PR\nto main", NAVY),
        ("3. CI: lint +\nsecurity + tests", BLUE), ("4. AI reviews\nCI logs", GREEN)]
row2 = [("5. Merge PR\n-> CD starts", NAVY), ("6. Deploy + run\nin QA", PURPLE),
        ("7. Approve ->\nDeploy + run\nPROD", AMBER), ("8. AI release notes\n+ notification", GREEN)]
flow(slide, row1, 1.6, 1.5, size=16)
arrow(slide, 11.9, 3.25, 0.4, 0.55, "down")
flow(slide, row2, 4.0, 1.5, size=16)
text(slide, 0.5, 5.9, 12.3, 1.0, "If any step fails, the pipeline stops and the team is notified. "
     "AI steps never block deployment (they only assist).", 16, color=GREY, align=PP_ALIGN.CENTER)

# 6. Branching -----------------------------------------------------------------
slide = new_slide("Branching Strategy", "Simple feature-branch flow",
                  "Developers never push directly to main. main always equals what is deployed.")
flow(slide, [("feature/<name>\nCI runs on push", GREY), ("Pull Request\nCI must pass", NAVY),
             ("main\nCD starts", BLUE), ("QA\nautomatic", PURPLE), ("PROD\nafter approval", ORANGE)],
     2.0, 1.5, size=16)
bullets(slide, 0.8, 4.1, 12, 3, [
    "feature/** and develop branches: CI only (no deployment)",
    "Pull request to main: CI must be green before merge (branch protection)",
    "Merge to main: full CD (QA -> approval -> PROD)",
    "concurrency setting: only one deployment at a time, never in parallel",
], 17)

# 7. CI flow -------------------------------------------------------------------
slide = new_slide("CI Workflow (ci.yml)", "Runs on every pull request and feature push",
                  "Three jobs. Quality checks first; bundle validation and AI review use its result.")
flow(slide, [("Checkout\nPython + Java", GREY), ("flake8\ncode style", BLUE), ("yamllint\nYAML files", BLUE),
             ("bandit\nsecurity scan", ORANGE), ("pytest\nlocal Spark", TEAL), ("Upload logs\nartifact", GREY)],
     1.5, 1.2, size=14)
panel(slide, 0.5, 3.1, 6.0, 3.9, "Job 2: Validate bundle", border=PURPLE)
bullets(slide, 0.7, 3.65, 5.7, 3.3, [
    "Installs the Databricks CLI",
    "databricks bundle validate -t qa",
    "databricks bundle validate -t prod",
    "Catches config errors before any deploy",
], 16)
panel(slide, 6.83, 3.1, 6.0, 3.9, "Job 3: AI review (optional)", border=GREEN)
bullets(slide, 7.03, 3.65, 5.7, 3.3, [
    "Runs when variable ENABLE_AI = true",
    "Downloads CI logs",
    "AI: CI build & test summary",
    "AI: GitHub workflow review (security, caching)",
    "continue-on-error: never blocks the pipeline",
], 16)

# 8. CD flow -------------------------------------------------------------------
slide = new_slide("CD Workflow (cd.yml)", "Runs when code is merged to main",
                  "QA and PROD use the SAME reusable workflow; only the target changes. PROD waits for a reviewer.")
flow(slide, [("CI\n(reused ci.yml)", BLUE), ("Deploy QA\nqa_catalog", PURPLE), ("Manual\napproval", AMBER),
             ("Deploy PROD\nprod_catalog", ORANGE), ("AI release\nreport", GREEN), ("Notify\nSlack / Teams", GREY)],
     1.5, 1.2, size=15)
panel(slide, 0.5, 3.1, 12.33, 3.9,
      "Reusable deploy workflow (reusable-databricks-deploy.yml) - same steps for QA and PROD", border=PURPLE)
flow(slide, [("Checkout", GREY), ("Install\nDatabricks CLI", NAVY), ("bundle\nvalidate", BLUE),
             ("bundle\ndeploy", PURPLE), ("bundle run\nsales_etl_job", ORANGE), ("Summary +\nupload logs", GREY)],
     3.8, 1.2, x0=0.8, width=11.7, size=14)
text(slide, 0.8, 5.4, 11.7, 1.4, "Write once, reuse for every environment. The 'prod' GitHub Environment has "
     "Required reviewers, so the PROD job pauses until someone approves.", 15, color=GREY)

# 9. Databricks ETL -------------------------------------------------------------
slide = new_slide("Databricks ETL Job - Medallion Architecture", "5 tasks, run one after another on serverless compute",
                  "Bronze = raw, Silver = clean, Gold = business summary. Validation stops the job if data is bad.")
flow(slide, [("00 Setup\ncatalog + schema", GREY), ("01 Bronze\nraw orders", BRONZE), ("02 Silver\nclean data", SILVER),
             ("03 Gold\nsales summary", GOLD), ("04 Validate\nquality gate", GREEN)], 1.5, 1.3, size=16)
table(slide, 0.5, 3.3, 12.33, [
    ["Layer", "Table", "What happens"],
    ["Bronze", "bronze_orders", "Load raw sample orders as-is"],
    ["Silver", "silver_orders", "Drop nulls/duplicates, remove qty/price <= 0, trim text, add amount"],
    ["Gold", "gold_sales_summary", "Orders, quantity and revenue per region and product"],
    ["Validate", "-", "Fail the job if null IDs, amount <= 0 or duplicate orders are found"],
], [1.6, 2.6, 8.13], 15)

# 10. Environments ------------------------------------------------------------
slide = new_slide("Environments and Free Edition Constraints", "One workspace, two catalogs",
                  "Databricks Free Edition gives one workspace, so QA and PROD are separated "
                  "with Unity Catalog catalogs.")
table(slide, 0.5, 1.4, 12.33, [
    ["Environment", "Bundle target", "Catalog", "Job name", "Approval"],
    ["QA", "qa", "qa_catalog", "[qa] Sales ETL Job", "Automatic"],
    ["PROD", "prod", "prod_catalog", "[prod] Sales ETL Job", "Required reviewer"],
], [2.2, 2.2, 2.4, 3.3, 2.23], 15)
table(slide, 0.5, 3.2, 12.33, [
    ["Free Edition constraint", "How we handle it"],
    ["Only one workspace", "Separate catalogs + bundle targets for QA and PROD"],
    ["Serverless compute only", "No cluster defined in the job -> runs on serverless"],
    ["No DBFS / external storage", "Unity Catalog managed tables"],
    ["Limited compute", "Small data, max_concurrent_runs = 1"],
    ["Limited outbound internet", "AI calls run on the GitHub runner, not in Databricks"],
], [4.5, 7.83], 15)

# 11. GenAI flow ---------------------------------------------------------------
slide = new_slide("GenAI Flow (scripts/ai_assistant.py)", "How one AI report is created",
                  "The AI is an assistant, not a gate. Secrets are removed before sending. If AI is down, a normal "
                  "report is still written and the pipeline passes.")
flow(slide, [("Collect input\nlogs / git / code", GREY), ("Redact secrets\ntokens, host, keys", ORANGE),
             ("Build prompt\nfixed sections", BLUE), ("Call Gemini\nretry + fallback", GREEN),
             ("Write Markdown\n+ run Summary", PURPLE)], 1.5, 1.3, size=15)
panel(slide, 0.5, 3.2, 6.0, 3.8, "Reliability", border=GREEN)
bullets(slide, 0.7, 3.75, 5.7, 3.2, [
    "Gemini models tried in order:",
    "- 3.7-flash -> 3.5-flash-lite -> 3.8-flash",
    "429 / 503: waits the time Gemini asks, then retries",
    "90 s timeout per request",
    "All fail -> fallback report, exit code 0",
], 16)
panel(slide, 6.83, 3.2, 6.0, 3.8, "Why Gemini (and not Ollama)?", border=BLUE)
bullets(slide, 7.03, 3.75, 5.7, 3.2, [
    "Company Ollama servers need GlobalProtect VPN",
    "VPN blocks personal GitHub -> conflict",
    "Gemini API is public: works on GitHub runners",
    "Free tier, key stored as secret GEMINI_API_KEY",
    "Ollama still supported: AI_PROVIDER=ollama",
], 16)

# 12. GenAI use cases ----------------------------------------------------------
slide = new_slide("GenAI Use Cases", "5 commands, each saves manual effort",
                  "For the demo show review-workflows and release-notes: both are quick and easy to understand.")
table(slide, 0.5, 1.4, 12.33, [
    ["Command", "Used in", "Input", "Output"],
    ["check", "CI + CD", "API key / servers", "Connectivity OK / FAIL"],
    ["summarize-logs", "CI + CD", "Lint, test, deploy logs", "Status, errors, root cause, fixes"],
    ["release-notes", "CD", "git history", "Highlights, fixes, changelog"],
    ["generate-docs", "CD", "src + bundle YAML", "Pipeline documentation"],
    ["review-workflows", "CI", ".github/workflows/*.yml", "Findings table by severity"],
    ["generate-workflow", "Local", "Plain-English request", "Draft workflow YAML"],
], [2.8, 1.8, 3.4, 4.33], 15)
text(slide, 0.5, 4.8, 12.33, 1.5, "Every AI report carries a note: 'Generated by AI. Review for accuracy before "
     "publishing.'  ->  a human always validates.", 16, color=GREY)

# 13. Security -----------------------------------------------------------------
slide = new_slide("Security Best Practices", "Security built into every step",
                  "Mention least privilege, secrets handling and scanning. These map to milestone M4.")
items = [
    ("Secrets", "Tokens only in GitHub Secrets,\nnever in code", NAVY),
    ("Least privilege", "permissions: contents: read", BLUE),
    ("SAST", "bandit scans Python code\non every PR", ORANGE),
    ("Redaction", "Tokens / keys masked before\nsending anything to AI", GREEN),
    ("Approvals", "PROD needs a required\nreviewer", AMBER),
    ("Safe inputs", "Inputs passed as env vars,\nSQL names validated", PURPLE),
]
for i, (name, desc, colour) in enumerate(items):
    col, row = i % 3, i // 3
    box(slide, 0.5 + col * 4.15, 1.5 + row * 2.8, 3.9, 2.4, f"{name}\n{desc}", colour, 20)

# 14. CI/CD best practices -----------------------------------------------------
slide = new_slide("CI/CD Best Practices Followed", "What makes this pipeline reliable",
                  "Pick 3-4 of these to highlight verbally.")
panel(slide, 0.5, 1.4, 6.0, 5.6, "Pipeline design", border=BLUE)
bullets(slide, 0.7, 1.95, 5.7, 5.0, [
    "Reusable workflow for QA and PROD",
    "Infrastructure as code (Asset Bundles)",
    "Fail fast: lint and tests before deploy",
    "timeout-minutes on every job",
    "concurrency: no parallel deployments",
    "pip caching for faster builds",
], 17)
panel(slide, 6.83, 1.4, 6.0, 5.6, "Operations", border=GREEN)
bullets(slide, 7.03, 1.95, 5.7, 5.0, [
    "Logs uploaded as artifacts for every run",
    "Deployment summary on the run page",
    "Data quality gate stops bad data",
    "Slack / Teams notification with result",
    "AI never blocks deployment",
    "Human review of all AI output",
], 17)

# 15. Needs / prerequisites ----------------------------------------------------
slide = new_slide("What Is Needed (Setup)", "One-time configuration",
                  "Everything is configured in GitHub Settings. No secret is stored in the repository.")
table(slide, 0.5, 1.4, 12.33, [
    ["Type", "Name", "Purpose"],
    ["Secret", "DATABRICKS_HOST", "Databricks workspace URL"],
    ["Secret", "DATABRICKS_TOKEN", "Personal access token for the CLI"],
    ["Secret", "GEMINI_API_KEY", "Free key from aistudio.google.com"],
    ["Secret (optional)", "NOTIFY_WEBHOOK_URL", "Slack / Teams incoming webhook"],
    ["Variable", "ENABLE_AI = true", "Turns the GenAI jobs on"],
    ["Variable (optional)", "AI_PROVIDER / GEMINI_MODEL", "Choose provider or first model"],
    ["Environment", "qa, prod", "prod has Required reviewers"],
], [3.0, 3.8, 5.53], 15)

# 16. Demo ---------------------------------------------------------------------
slide = new_slide("Live Demo Plan", "What will be shown",
                  "Keep reports pre-generated in ai_reports/ in case the free AI tier is busy during the demo.")
flow(slide, [("1. Push to\nfeature branch", GREY), ("2. CI green\nin Actions", BLUE),
             ("3. AI summary\non run page", GREEN),
             ("4. Merge ->\nQA deploy", PURPLE), ("5. Approve ->\nPROD", AMBER), ("6. Tables in\nDatabricks", ORANGE)],
     1.6, 1.4, size=15)
panel(slide, 0.5, 3.5, 12.33, 3.5, "Local AI demo (VPN off)", border=GREEN)
text(slide, 0.8, 4.05, 11.8, 2.9,
     '$env:AI_PROVIDER = "gemini"\n'
     '$env:GEMINI_API_KEY = "<key>"\n'
     "py scripts/ai_assistant.py review-workflows --output ai_reports/workflow_review.md\n"
     "py scripts/ai_assistant.py release-notes --max-commits 10", 16, color=DARK)

# 17. Benefits -----------------------------------------------------------------
slide = new_slide("Benefits and Outcome", "What the business gets",
                  "Close with the value: faster, safer releases and less manual work.")
items = [
    ("Faster releases", "One push deploys\nQA automatically", BLUE),
    ("Fewer defects", "Tests + quality gate\nbefore PROD", GREEN),
    ("Controlled PROD", "Approval + audit trail\nin GitHub", AMBER),
    ("Less manual work", "AI writes summaries,\nnotes and docs", PURPLE),
]
for i, (name, desc, colour) in enumerate(items):
    box(slide, 0.5 + i * 3.15, 1.8, 2.9, 2.6, f"{name}\n{desc}", colour, 20)
text(slide, 0.5, 5.0, 12.33, 1.5, "Future scope: service principals (OAuth), more environments, "
     "AI-suggested fixes as PR comments, data quality dashboards.", 17, color=GREY, align=PP_ALIGN.CENTER)

# 18. Thank you ---------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()
text(slide, 0.5, 2.6, 12.33, 1.2, "Thank You", 48, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
text(slide, 0.5, 3.8, 12.33, 0.8, "Questions?", 24, color=RGBColor(0xD0, 0xDC, 0xF0), align=PP_ALIGN.CENTER)

prs.save(OUTPUT)
print(f"Saved {OUTPUT}")
