# PDD Forge — Product & Engineering Plan (Part 2)

> Continuation of the implementation plan. See [Part 1](file:///C:/Users/Natibe%20Dijital/.gemini/antigravity/brain/167135be-b84e-46be-9659-23401e137a65/implementation_plan.md) for sections 1–11.

---

## 12. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend API** | Python 3.11+ / FastAPI | Async support, strong PDF/ML ecosystem, rapid prototyping |
| **PDF Parsing** | PyMuPDF (fitz) + pdfplumber | PyMuPDF for speed; pdfplumber for table extraction |
| **Layout Analysis** | Docling (IBM) — optional | Deep layout parsing for complex PDDs with nested tables/diagrams |
| **LLM Provider** | OpenAI GPT-4o (primary) / Claude 3.5 Sonnet (fallback) | GPT-4o for structured outputs; Claude for complex reasoning |
| **LLM Orchestration** | LangChain (lightweight) or direct API calls | Structured output, retry logic, prompt management |
| **XAML Generation** | Jinja2 + lxml | Template-based XML composition; lxml for validation |
| **Excel Generation** | openpyxl | Config.xlsx creation |
| **Validation** | Pydantic v2 | IR schema validation, type safety |
| **Frontend** | React + TypeScript + Vite | Modern SPA; fast dev iteration |
| **File Handling** | ZIP archive (Python zipfile) | Standard UiPath project sharing format |
| **Storage** | PostgreSQL (metadata) + S3/local filesystem (files) | Structured + blob storage |
| **Task Queue** | Celery + Redis (if async processing needed) | Long-running PDD processing |
| **Containerization** | Docker + Docker Compose | Consistent deployment |
| **Testing** | pytest + UiPath Studio validation (manual) | Automated + manual XAML validation |

### Stack Decision: Why NOT .NET?

UiPath itself runs on .NET, which might suggest a .NET backend. However:
- Python has superior PDF parsing libraries
- Python's LLM ecosystem (LangChain, OpenAI SDK) is more mature
- XAML generation is template-based (language-agnostic)
- The product does not need to interact with UiPath runtime APIs

If Orchestrator API integration becomes critical in later phases, a .NET microservice can be added.

---

## 13. MVP Scope

### 13.1 MVP Definition

> **Goal:** Accept a standard PDD PDF → produce a valid REFramework (Queue) project ZIP that opens in UiPath Studio without errors.

### 13.2 MVP Feature Matrix

| Feature | In MVP | Notes |
|---|---|---|
| PDF upload (single file, ≤50 pages) | ✅ | |
| Automatic section extraction | ✅ | With user review step |
| Business rule extraction | ✅ | Extracted as annotations/comments, not executable logic |
| Step-to-workflow mapping | ✅ | 1 step = 1 invoked workflow file |
| REFramework (Queue) template | ✅ | Single template |
| Config.xlsx generation | ✅ | Settings + Constants + Assets sheets |
| project.json generation | ✅ | Valid for Studio 2023.10+ |
| XAML file generation (skeleton) | ✅ | Sequence-based, with TODO placeholders |
| Generation report (HTML) | ✅ | Confidence scores + traceability |
| Traceability matrix | ✅ | PDD section → generated file mapping |
| Web UI (upload + download) | ✅ | Minimal but functional |
| Human review of extracted sections | ✅ | |
| Human review of IR | ❌ | v1.1 |
| Multiple templates | ❌ | v1.1 |
| Existing project injection | ❌ | v1.1 |
| Flowchart image extraction | ❌ | v2 |
| Orchestrator API integration | ❌ | v2 |
| Multi-PDD / batch processing | ❌ | v2 |
| User accounts / project history | ❌ | v2 |

### 13.3 MVP User Flow

```
1. User opens web UI
2. User uploads PDD PDF
3. System extracts text and identifies sections (15–60 seconds)
4. User reviews extracted sections on screen
   - Can re-label, merge, or add missing content
5. User confirms sections → system performs semantic analysis (30–90 seconds)
6. User sees summary: extracted steps, rules, exceptions, config items
7. User selects output options:
   - Process name
   - Studio version target (dropdown)
   - Template: REFramework Queue (only option in MVP)
8. User clicks "Generate"
9. System generates project (10–30 seconds)
10. User downloads ZIP
11. User also downloads generation report (HTML)
12. User opens ZIP in UiPath Studio
```

---

## 14. Future Scope

### v1.1 (Month 2–3 post-MVP)
- REFramework (Tabular) + Linear Process templates
- IR review/edit UI
- Existing empty project injection
- PDD quality scoring with improvement suggestions
- Generation history (per-session, no auth)

### v2.0 (Month 4–6)
- Flowchart image extraction via vision models
- Orchestrator API integration (queue/asset provisioning)
- User accounts and project persistence
- Custom template authoring (user-defined templates)
- Multi-language PDD support (starting with Turkish, given user context)
- Coded Workflow (.cs) generation option alongside XAML
- Batch PDD processing

### v3.0 (Month 7–12)
- Fine-tuned extraction model for PDD-specific parsing
- Selector suggestion based on application screenshots
- Integration with UiPath Studio plugin (direct import)
- PDD diff detection (re-generate on PDD update)
- Team collaboration features
- CI/CD pipeline integration for generated projects

---

## 15. Development Phases

### Phase 0: Foundation (Week 1–2)

| Task | Output | Owner Role |
|---|---|---|
| Set up Python project structure | FastAPI skeleton, Docker setup | Backend |
| Create XAML fragment library | 10 core validated fragments | UiPath + Backend |
| Build REFramework base template | Template folder with Jinja2 files | UiPath + Backend |
| Define IR JSON schema | Pydantic models | Backend |
| Set up React frontend scaffold | Upload + download UI | Frontend |

### Phase 1: PDF Parsing Pipeline (Week 3–4)

| Task | Output |
|---|---|
| Implement PDF text extraction (PyMuPDF) | Raw text with page numbers |
| Implement table extraction (pdfplumber) | Structured tables |
| Implement LLM-based section classifier | Labeled sections with confidence |
| Build section review UI | Editable section list |
| Test with 5+ real PDD samples | Accuracy metrics |

### Phase 2: Semantic Analysis (Week 5–6)

| Task | Output |
|---|---|
| Implement step extraction prompt chain | Ordered step list in IR |
| Implement business rule extraction | Structured rules in IR |
| Implement exception classification | BRE vs SysEx in IR |
| Implement config extraction | Settings/Constants/Assets in IR |
| Build IR validator (Pydantic) | Validation report |
| Test with 5+ PDDs | IR accuracy metrics |

### Phase 3: Project Generation (Week 7–8)

| Task | Output |
|---|---|
| Implement project.json generator | Valid project.json |
| Implement XAML template renderer | Skeleton .xaml files |
| Implement Config.xlsx generator | Populated Config.xlsx |
| Implement folder structure builder | Complete project folder |
| Implement ZIP packaging | Downloadable ZIP |
| Validate: open 10 generated projects in Studio | 100% open success rate |

### Phase 4: Integration & Polish (Week 9–10)

| Task | Output |
|---|---|
| Wire end-to-end pipeline | Upload → Download flow |
| Build generation report | HTML report with traceability |
| Implement error handling and edge cases | Robust error messages |
| Performance optimization | < 2 min total processing time |
| User acceptance testing with 3 RPA developers | Feedback incorporation |

---

## 16. UI Screens and User Flow

### Screen 1: Upload & Configure

```
┌─────────────────────────────────────────────────┐
│  PDD Forge                                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │                                         │    │
│  │     📄 Drop your PDD here               │    │
│  │        or click to browse               │    │
│  │                                         │    │
│  │     Supported: PDF (max 50 pages)       │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  Process Name: [________________________]       │
│                                                 │
│  Template:     [REFramework (Queue)     ▼]      │
│                                                 │
│  Studio Version: [2023.10             ▼]        │
│                                                 │
│  ☐ Inject into existing project                 │
│    [Select project folder...]                   │
│                                                 │
│              [ Parse PDD → ]                    │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Screen 2: Section Review

```
┌─────────────────────────────────────────────────┐
│  Section Review                    [Back] [Next]│
├─────────────────────────────────────────────────┤
│                                                 │
│  PDD Quality Score: ██████████░░ 78/100         │
│                                                 │
│  ┌──────────────┬────────────┬────────────────┐ │
│  │ Section      │ Confidence │ Pages          │ │
│  ├──────────────┼────────────┼────────────────┤ │
│  │ ✅ Scope     │ 92%        │ 3-4            │ │
│  │ ✅ Steps     │ 85%        │ 5-12           │ │
│  │ ⚠️ Rules     │ 61%        │ 13-15          │ │
│  │ ✅ Exceptions│ 88%        │ 16-17          │ │
│  │ ❌ Config    │ 35%        │ Not found      │ │
│  │ ✅ Apps      │ 90%        │ 4, 8           │ │
│  └──────────────┴────────────┴────────────────┘ │
│                                                 │
│  [Click any section to review and edit]         │
│                                                 │
│  ⚠️ Config section not found.                   │
│     [Add manually] [Skip — use defaults]        │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Screen 3: Extraction Summary

```
┌─────────────────────────────────────────────────┐
│  Extraction Summary                [Back] [Gen] │
├─────────────────────────────────────────────────┤
│                                                 │
│  📋 Steps (12 extracted)                        │
│  ├── 1. Login to SAP                            │
│  ├── 2. Navigate to Transaction VA01            │
│  ├── 3. Enter customer data                     │
│  ├── ...                                        │
│                                                 │
│  📏 Business Rules (5 extracted)                │
│  ├── IF order_amount > 10000 THEN require_mgr   │
│  ├── IF customer_type == "VIP" THEN priority     │
│  ├── ...                                        │
│                                                 │
│  ⚠️ Exceptions (3 extracted)                    │
│  ├── BRE: Invalid customer ID                   │
│  ├── SysEx: SAP connection timeout              │
│  ├── ...                                        │
│                                                 │
│  ⚙️ Configuration (8 items)                     │
│  ├── SAP_URL: [extracted]                       │
│  ├── MaxRetries: 3                              │
│  ├── ...                                        │
│                                                 │
│              [ Generate Project → ]             │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Screen 4: Generation Result

```
┌─────────────────────────────────────────────────┐
│  Generation Complete ✅              [New PDD]  │
├─────────────────────────────────────────────────┤
│                                                 │
│  📁 Generated Project Structure:                │
│  ├── project.json                               │
│  ├── Main.xaml                                  │
│  ├── Process.xaml                               │
│  ├── Framework/                                 │
│  │   ├── InitAllSettings.xaml                   │
│  │   ├── InitAllApplications.xaml               │
│  │   ├── GetTransactionData.xaml                │
│  │   ├── SetTransactionStatus.xaml              │
│  │   ├── CloseAllApplications.xaml              │
│  │   └── KillAllProcesses.xaml                  │
│  ├── Process/                                   │
│  │   ├── Step01_LoginToSAP.xaml                 │
│  │   ├── Step02_NavigateVA01.xaml               │
│  │   └── ...                                   │
│  └── Data/                                      │
│      └── Config.xlsx                            │
│                                                 │
│  ⚠️ 4 TODO items require attention              │
│  ⚠️ 2 low-confidence extractions flagged        │
│                                                 │
│  [📥 Download Project ZIP]                      │
│  [📄 Download Generation Report]                │
│  [📊 View Traceability Matrix]                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 17. Testing and Quality Strategy

### 17.1 Automated Testing

| Test Type | Tool | Scope |
|---|---|---|
| Unit tests | pytest | IR construction, XAML fragment rendering, Config generation |
| Integration tests | pytest + test PDDs | End-to-end pipeline with 10+ sample PDDs |
| XAML validation | lxml + custom XSD-like rules | Every generated .xaml is well-formed XML with required namespaces |
| project.json validation | jsonschema | Schema compliance |
| Snapshot tests | pytest-snapshot | Generated output stability across code changes |

### 17.2 Manual Validation (Critical)

| Test | Method | Frequency |
|---|---|---|
| **Studio Open Test** | Open every generated ZIP in UiPath Studio; verify no errors | Every release |
| **Studio Run Test** | Run Main.xaml in Studio (will fail at selectors, but framework states should transition) | Every release |
| **Developer Review** | 3 RPA developers review generated projects for structural correctness | Monthly |
| **PDD Diversity Test** | Test with 20+ PDDs from different organizations/formats | Quarterly |

### 17.3 Golden Test Suite

Maintain a set of 10 "golden" PDD–project pairs:
- Each pair has a known-good PDD and an expected project structure
- CI pipeline generates project from PDD and compares structure to expected output
- Structural diff (file tree + key XAML elements), not byte-level diff

### 17.4 LLM Output Testing

| Concern | Strategy |
|---|---|
| Extraction consistency | Run same PDD 5x; measure extraction variance (target: < 10% variance) |
| Hallucination detection | Compare extracted steps against PDD text using embedding similarity |
| Regression | Pin LLM model version; re-run golden suite on model updates |

---

## 18. Success Criteria

### 18.1 MVP Success Criteria

| Criterion | Target | Measurement |
|---|---|---|
| Project opens in Studio | 100% | Automated test |
| Section extraction accuracy | ≥ 85% F1 | Manual annotation comparison |
| Step extraction accuracy | ≥ 75% F1 | Manual annotation comparison |
| Generation time (50-page PDD) | < 2 minutes | Performance test |
| Developer satisfaction | ≥ 7/10 | Survey of 5+ RPA developers |
| Time saved vs. manual | ≥ 50% | Timed comparison study |

### 18.2 v1.0 Success Criteria

| Criterion | Target |
|---|---|
| Works with ≥ 3 PDD formats without config changes | Tested with real client PDDs |
| REFramework state machine transitions work in Studio | Manual run test |
| Config.xlsx is correctly read by InitAllSettings.xaml | Manual run test |
| Zero data loss: every PDD section appears in at least one artifact | Traceability matrix check |

---

## 19. Open Questions

> [!IMPORTANT]
> These questions should be answered before or during Phase 0.

| # | Question | Impact | Suggested Default |
|---|---|---|---|
| 1 | **Do you have access to 10+ real PDD samples for training/testing?** | Critical for extraction accuracy | Minimum 5 required for MVP |
| 2 | **Which UiPath Studio version(s) should be supported?** | Affects XAML format and project.json schema | 2023.10+ (Windows + cross-platform) |
| 3 | **Should the tool support UiPath Coded Workflows (.cs) in addition to XAML?** | Doubles the generation surface area | XAML only for MVP |
| 4 | **Is Orchestrator integration in scope for MVP?** | Adds API dependency and auth complexity | No — generate queue/asset names only |
| 5 | **What is the deployment target?** Self-hosted, cloud, or desktop? | Architecture and security implications | Self-hosted Docker for MVP |
| 6 | **Is multi-language PDD support needed?** | Affects LLM prompt design | English only for MVP |
| 7 | **What is the expected PDD page count range?** | Affects chunking strategy and token budget | 10–80 pages |
| 8 | **Do PDDs contain embedded flowchart images that are critical?** | Determines vision model priority | Flag-and-skip for MVP |
| 9 | **Are there custom UiPath activity packages in use?** | Cannot generate activities for unknown packages | Standard activities only |
| 10 | **What LLM provider is acceptable?** (OpenAI, Azure OpenAI, Anthropic, self-hosted) | API keys, data privacy, cost | Azure OpenAI for enterprise data privacy |

---

## 20. Final Recommendation

### Verdict: **Build it — as a semi-automated scaffold generator.**

This product is **technically feasible and commercially valuable**, provided the scope is correctly bounded:

**Do build:**
- A robust PDD parsing pipeline using LLMs for understanding (not generation)
- A template-based XAML generation engine with validated fragments
- A human-in-the-loop review flow at two checkpoints (sections + IR)
- A clear "scaffold, not solution" positioning

**Do not build (yet):**
- Full automation with no human review
- Selector generation
- Production deployment of generated bots
- Custom activity support

**Key insight:** The value is in the **80% scaffolding** — project structure, workflow wiring, Config.xlsx population, and annotation injection. The remaining **20% (selectors, expressions, business logic implementation)** is where the RPA developer adds real value. This ratio makes the product a legitimate accelerator without being a dangerous false promise.

### Risk/Reward Assessment

| Factor | Rating |
|---|---|
| Technical feasibility | ⭐⭐⭐⭐ (4/5) |
| Market need | ⭐⭐⭐⭐⭐ (5/5) |
| Competitive moat | ⭐⭐⭐ (3/5) — UiPath could build this natively |
| Development complexity | ⭐⭐⭐⭐ (4/5 — high, but manageable) |
| Time to MVP | ⭐⭐⭐⭐ (4/5 — 10 weeks is realistic) |

---

## 21. Recommended Architecture Decisions

| # | Decision | Recommendation | Alternative Considered | Why Not |
|---|---|---|---|---|
| 1 | XAML generation | Template composition (Jinja2) | LLM-generated XAML | LLM XAML is structurally unreliable; no public schema to validate against |
| 2 | LLM role | Understanding/extraction only | Also code generation | Separation of concerns; testability; determinism |
| 3 | IR design | Flat JSON with step array | Graph-based IR | Flat is simpler; graph adds complexity without MVP benefit |
| 4 | Frontend | React SPA | Desktop app (Electron) | Web is more accessible; no install barrier |
| 5 | Backend language | Python | C# / .NET | Python PDF/ML ecosystem is superior |
| 6 | Template format | Jinja2 files in filesystem | Database-stored templates | Filesystem is version-controllable and auditable |
| 7 | Output format | ZIP file | Direct filesystem write | ZIP is portable; avoids permission issues |
| 8 | LLM provider | Azure OpenAI (enterprise) or OpenAI (prototype) | Self-hosted LLM | Self-hosted adds ops burden; quality gap is significant |
| 9 | Processing model | Synchronous (MVP) → Async (v1.1) | Async from day 1 | Synchronous is simpler; PDDs process in < 2 min |
| 10 | XAML validation | Custom rules + lxml well-formedness | Full XSD validation | No public XSD exists; custom rules are more practical |

---

## 22. 30-Day Prototype Plan

> [!NOTE]
> This plan targets a **working demo** — not the full MVP. The goal is to prove the core pipeline works end-to-end with a single PDD.

### Week 1: Foundation

| Day | Task | Deliverable |
|---|---|---|
| 1 | Set up Python project (FastAPI, pyproject.toml, Docker) | Running empty API |
| 2 | Implement PDF text extraction (PyMuPDF) | Text output from sample PDD |
| 3 | Implement table extraction (pdfplumber) | Table data from sample PDD |
| 4 | Design IR Pydantic schema | `models/ir.py` |
| 5 | Reverse-engineer REFramework XAML (open in text editor, annotate) | XAML template catalog doc |

### Week 2: Parsing & Extraction

| Day | Task | Deliverable |
|---|---|---|
| 6–7 | Build LLM section classifier (few-shot prompt, GPT-4o) | Section labels for sample PDD |
| 8–9 | Build LLM step extractor (structured output) | Step list in IR format |
| 10 | Build LLM rule/exception extractor | Rules + exceptions in IR |

### Week 3: Generation

| Day | Task | Deliverable |
|---|---|---|
| 11 | Create Jinja2 XAML fragment templates (5 core fragments) | Template files |
| 12 | Build project.json generator | Valid project.json |
| 13 | Build Main.xaml generator (REFramework state machine) | Main.xaml that opens in Studio |
| 14 | Build Process.xaml + step workflow generators | Process.xaml + Step01.xaml...StepN.xaml |
| 15 | Build Config.xlsx generator | Populated Config.xlsx |

### Week 4: Integration & Demo

| Day | Task | Deliverable |
|---|---|---|
| 16 | Wire end-to-end: PDF → IR → Project ZIP | CLI tool that converts PDD to ZIP |
| 17 | Build minimal web UI (upload + download) | Working web page |
| 18 | Generate from 3 different PDDs; fix issues | 3 valid projects |
| 19 | Build generation report (simple HTML) | Report with traceability |
| 20 | Demo prep; documentation | Working prototype + demo script |

### Week 4 Exit Criteria

- [ ] Upload any standard PDD PDF → get a ZIP
- [ ] ZIP opens in UiPath Studio 2023.10+ without errors
- [ ] Main.xaml shows REFramework state machine structure
- [ ] Process.xaml contains Invoke calls to step workflows
- [ ] Config.xlsx has populated Settings/Constants/Assets sheets
- [ ] Each generated workflow has annotations tracing back to PDD sections
- [ ] Generation report lists all extracted items with confidence scores

### Prototype Limitations (Acceptable)

- No section review UI (CLI bypass)
- Single template only (REFramework Queue)
- No existing project injection
- No persistent storage
- No error recovery / retry
- English PDDs only
- Tested with ≤ 5 PDDs

---

## Appendix: Safeguards Not Mentioned in Original Requirements

| Safeguard | Rationale |
|---|---|
| **PDD data privacy** | PDDs may contain sensitive business processes. All LLM calls should use Azure OpenAI (enterprise) or equivalent with data processing agreements. No PDD data should be stored permanently unless explicitly opted in. |
| **Version pinning for LLM models** | LLM behavior changes across versions. Pin model version (e.g., `gpt-4o-2024-08-06`) and re-validate golden test suite on every model update. |
| **Generation audit trail** | Log every generation run: input hash, IR snapshot, template used, output hash, LLM model version, timestamp. Essential for debugging and compliance. |
| **Rate limiting** | Prevent abuse and control LLM costs. Implement per-user rate limits. |
| **XAML injection prevention** | If PDD text contains XML/XAML-like content, it must be escaped before injection into templates. Failure to do so could produce corrupted workflows. |
| **Telemetry (opt-in)** | Track extraction accuracy, generation success rate, and user corrections to improve the system over time. Must be opt-in with clear data handling policy. |
| **Graceful degradation** | If LLM API is unavailable, the system should still allow manual section tagging and template-only generation (without semantic extraction). |
| **Export to SDD** | Generate a Solution Design Document (SDD) skeleton alongside the project, bridging the gap between PDD and implementation documentation. |
