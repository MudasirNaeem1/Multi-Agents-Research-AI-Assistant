# 🔬 Multi-Agent Research Assistant

> An intelligent, fully automated research pipeline powered by **LangChain**, **LangGraph**, and **Groq LLaMA 3.3 70B** — turning any topic into a structured, critically reviewed research report in under a minute.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-FF6B35?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-F55036?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Cost](https://img.shields.io/badge/Cost-$0.00%20Free%20Tier-brightgreen?style=for-the-badge)

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [System Architecture](#-system-architecture)
- [Agent Pipeline](#-agent-pipeline)
  - [Agent 1 — Search Agent](#agent-1--search-agent)
  - [Agent 2 — Reader Agent](#agent-2--reader-agent)
  - [Agent 3 — Writer Agent](#agent-3--writer-agent)
  - [Agent 4 — Critic Agent](#agent-4--critic-agent)
- [Frontend Interface](#-frontend-interface)
- [Tech Stack](#-tech-stack)
- [Why 4 Agents Instead of 1?](#-why-4-agents-instead-of-1)
- [LangChain vs LangGraph — When We Use What](#-langchain-vs-langgraph--when-we-use-what)
- [Cost Analysis](#-cost-analysis)
- [Comparison: Our System vs Existing LLMs](#-comparison-our-system-vs-existing-llms)
- [Limitations & Future Enhancements](#-limitations--future-enhancements)
- [Setup & Installation](#-setup--installation)

---

## 🧠 Overview

The **Multi-Agent Research Assistant** automates the complete cycle of online research:

```
User Query → Search the Web → Read Full Pages → Write Report → Critically Review
```

A user types any research topic, clicks **Run**, and receives a professionally structured research report - with sources and an independent critic score — **without any manual intervention**.

Built entirely on **free-tier, open-source tools**, this system demonstrates production-grade Agentic AI for students and researchers at zero cost.

---

## ❗ Problem Statement

Traditional research is manual, fragmented, and slow. A researcher must:

- Search multiple engines and databases manually
- Visit and read each webpage individually
- Synthesize scattered information into a coherent report
- Self-evaluate or seek peer review for quality assurance

**This can take several hours per topic.** Existing AI tools (ChatGPT, Gemini, Claude) are single-model systems with key limitations:

| Limitation | Impact |
|---|---|
| No real-time web search (free tier) | Outdated, knowledge-cutoff-bound responses |
| No full-page scraping | Only snippets retrieved, not full article content |
| No separation of concerns | One model handles all tasks — quality drops |
| No self-critique mechanism | No scoring or quality evaluation |
| Paid at scale | API costs accumulate fast |

---

## 🏗 System Architecture

The system follows a **linear sequential pipeline**:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Agent 1    │    │  Agent 2    │    │  Agent 3    │    │  Agent 4    │
│  SEARCH     │───▶│  READER     │───▶│  WRITER     │───▶│  CRITIC     │
│             │    │             │    │             │    │             │
│ DuckDuckGo  │    │ trafilatura │    │ LangChain   │    │ LangChain   │
│ Direct Call │    │ LangGraph   │    │ LCEL Chain  │    │ LCEL Chain  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                  │                  │                  │
  URLs + Snippets    Full Page Text    Markdown Report    Score + Feedback
```

Each agent:
- Has a **dedicated Groq API key** (rate limit isolation)
- Handles **one specific stage** of research
- Passes its output as input to the next agent

---

## 🤖 Agent Pipeline

### Agent 1 - Search Agent

**Framework:** Direct Tool Call (no LLM loop)  
**Tool:** DuckDuckGo (`ddgs` library) - no API key, no cost  
**Model:** None (deterministic tool call)

- **Input:** User's research topic
- **Output:** 10 results — each with Title, URL, and content snippet

> **Why no LLM here?** Wrapping search in a React agent loop added 60-120 seconds of delay with zero benefit. A direct tool call drops this step from 2 minutes to under **3 seconds**.

---

### Agent 2 - Reader Agent

**Framework:** LangGraph React (Reason + Act loop)  
**Model:** `llama-3.3-70b-versatile` via Groq  
**API Key:** `GROQ_API_KEY_2`

Receives all 10 URLs from Agent 1 and scrapes full page content using a **3-layer extraction strategy**:

| Layer | Library | Best For |
|-------|---------|----------|
| **Layer 1** | `trafilatura` | News articles and blog posts |
| **Layer 2** | `readability-lxml` | Structured HTML pages (Mozilla Readability) |
| **Layer 3** | `BeautifulSoup4` | Final fallback — all other page types |

- **Input:** List of 10 URLs from Agent 1
- **Output:** Full raw text extracted from the most relevant web pages

> **Why LangGraph here?** Scraping requires reasoning - the agent must decide which URLs are scrapeable (skipping social media, login walls, PDFs), call the tool multiple times, and combine results. LangGraph's React loop handles this automatically.

---

### Agent 3 - Writer Agent

**Framework:** LangChain LCEL Chain (`prompt | llm | output_parser`)  
**Model:** `llama-3.3-70b-versatile` via Groq  
**API Key:** `GROQ_API_KEY_3`

Receives combined search results and scraped content, then writes a **structured Markdown research report**:

```
📄 Report Structure
├── Introduction         — Overview of the topic
├── Key Findings         — Minimum 3 well-explained points with evidence
├── Conclusion           — Summary and implications
└── Sources              — All URLs discovered during research
```

> ⚠️ The system prompt **strictly instructs the Writer to use only provided data** - never its own training knowledge - preventing hallucinated sources.

---

### Agent 4 - Critic Agent

**Framework:** LangChain LCEL Chain  
**Model:** `llama-3.3-70b-versatile` via Groq  
**API Key:** `GROQ_API_KEY_4`

Independently reviews the generated report using a **fair scoring rubric**:

| Score | Criteria | Verdict |
|-------|----------|---------|
| **9-10** | Well structured, relevant, covers key points, has sources | ✅ Excellent |
| **7-8** | Good content but missing some depth or sources | 🟡 Good |
| **5-6** | Relevant but poorly structured or thin content | 🟠 Fair |
| **< 5** | Content is completely irrelevant or incorrect | ❌ Poor |

> Having a **separate Critic prevents self-evaluation bias** - a Writer grading its own output always produces inflated 9–10 scores.

---

## 🖥 Frontend Interface

Built with **Streamlit** - a clean, dark-themed interactive web UI:

- **Research Studio tab** - Real-time pipeline status cards (Waiting / Running / Done) for each agent
- **Agent Flow Diagram tab** - Interactive visual flowchart of the pipeline architecture
- **Live spinners** updating as each agent completes
- **Downloadable `.md` report** and formatted Critic feedback panel

---

## 🛠 Tech Stack

| Tool / Library | Category | Purpose |
|---|---|---|
| **LangChain** | AI Framework | Prompts, LCEL chains, output parsers, tool decorators |
| **LangGraph** | Agent Orchestration | React loop for multi-step tool-calling agents |
| **Groq API** | LLM Inference | Free-tier cloud inference at 250–280 tokens/sec |
| **LLaMA 3.3 70B Versatile** | Language Model | Meta's open-source model with excellent tool-use & reasoning |
| **DuckDuckGo (`ddgs`)** | Web Search | Free, no-API-key real-time search |
| **trafilatura** | Web Scraping | Primary content extractor for articles/blogs |
| **readability-lxml** | Web Scraping | Secondary extractor (Mozilla Readability algorithm) |
| **BeautifulSoup4** | Web Scraping | Final fallback HTML parser |
| **Streamlit** | Web Interface | Interactive UI with real-time agent status |

---

## 🧩 Why 4 Agents Instead of 1?

| Concern | Single Agent | 4 Agents |
|---------|-------------|----------|
| **Rate Limits** | All operations hit one key → daily limit hit after ~5 searches | 4 keys × 4 accounts → 4× the daily token budget |
| **Quality** | Mixing search + scrape + write + critique in one prompt causes confusion | Each agent has one focused job and a specialized system prompt |
| **Bias** | Writer grades its own output - always scores 9-10 | Independent Critic uses a separate LLM call → honest evaluation |
| **Debugging** | Hard to tell which step failed in a monolithic prompt | Each step's output is logged - easy to trace failures |

---

## ⚙️ LangChain vs LangGraph - When We Use What

| | Agent 1 (Search) | Agent 2 (Reader) | Agents 3 & 4 (Writer/Critic) |
|---|---|---|---|
| **Framework** | None (direct call) | LangGraph React | LangChain Chain |
| **LLM involved?** | ❌ No | ✅ Yes | ✅ Yes |
| **Tool calls** | 1 × `web_search` | 3 × `scrape_url` | None |
| **Why this framework** | Speed - no LLM overhead | Needs multi-step tool loop | Single-shot text generation |

---

## 💰 Cost Analysis

### Current Stack — Free Tier

| Component | Provider | Cost |
|-----------|----------|------|
| LLM Inference (Agents 2, 3, 4) | Groq - LLaMA 3.3 70B | **FREE** (4 accounts × 500K tokens/day) |
| Web Search (Agent 1) | DuckDuckGo via `ddgs` | **FREE** (no API key required) |
| Web Scraping (Agent 2) | Direct HTTP (trafilatura/BS4) | **FREE** |
| Web UI | Streamlit | **FREE** (open-source) |
| **TOTAL DAILY COST** | | **$0.00** |

### Per-Run Token Consumption

| Agent | Input Tokens | Output Tokens | Notes |
|-------|-------------|--------------|-------|
| Agent 1 — Search | 0 | 0 | Direct tool call, no LLM |
| Agent 2 — Reader | ~3,000 | ~600 | 3× tool-call loop |
| Agent 3 — Writer | ~4,000 | ~1,200 | Combined research as input |
| Agent 4 — Critic | ~1,800 | ~300 | Report text as input |
| **TOTAL PER RUN** | **~8,800** | **~2,100** | **~10,900 tokens total** |

### If Scaled to Paid Production

At Groq's paid rate ($0.59/1M input, $0.79/1M output):

| Daily Runs | Monthly Runs | Monthly Cost |
|-----------|-------------|-------------|
| 10/day | ~300 | ~$2.07 |
| 50/day | ~1,500 | ~$10.35 |
| 200/day | ~6,000 | ~$41.40 |

**Cost per research report: < $0.01 (less than 1 cent)**

### Why DuckDuckGo Over SerpAPI?

| Factor | SerpAPI (Google) | DuckDuckGo (Current) |
|--------|-----------------|----------------------|
| Cost | $25/mo for 1,000 searches | **$0.00** |
| API Key | Required (paid) | Not required |
| Result Quality | Marginally better for niche/commercial | Equivalent for research topics |
| Monthly cost at 200 runs/day | ~$120/mo | **$0.00** |

For broad research topics (AI, climate, healthcare), DuckDuckGo returns the same authoritative sources as Google. The $120/month saving with zero quality tradeoff makes it the clear choice.

---

## 📊 Comparison: Our System vs Existing LLMs

| Feature | Our System | ChatGPT / Gemini / Claude |
|---------|-----------|--------------------------|
| **Architecture** | 4 specialized agents | Single model |
| **Real-time web search** | ✅ Always (free) | ⚠️ Paid tiers only |
| **Full-page scraping** | ✅ Entire articles (3-layer) | ❌ Snippets only |
| **Self-critique & scoring** | ✅ Dedicated Critic Agent | ❌ Not built-in |
| **Customizable** | ✅ Every prompt/tool/model | ❌ Fixed by provider |
| **Rate limit strategy** | 4 separate API keys | Single shared key |
| **Cost** | **$0** (free tier) | Paid for advanced features |
| **Open Source** | ✅ Full transparency | ❌ Black box |

> **Most significant differentiator:** While ChatGPT and Gemini can retrieve search snippets (on paid tiers), they **cannot extract full webpage content**. Our Reader Agent scrapes entire articles - thousands of words of context — dramatically improving report quality and depth.

---

## ⚠️ Limitations & Future Enhancements

### Current Limitations

- Groq free tier: 14,400 requests/day per key - heavy usage may hit limits
- Agent 2 currently scrapes only selected URLs - multiple parallel scrapes would improve depth
- No persistent memory between sessions - each query starts fresh
- Currently optimized for **English-language** queries and sources

### Planned Future Enhancements

- [ ] Scrape top 3–5 URLs **simultaneously using async** for richer content
- [ ] Auto-generate **APA/IEEE citations** from scraped sources
- [ ] Allow downloading final report as a **formatted PDF**
- [ ] Add **LangChain memory** to support follow-up research questions
- [ ] Add a **pre-pipeline query refinement agent** to expand user queries
- [ ] Multi-language support

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10+
- 4 separate Groq accounts (free) for API keys

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/multi-agent-research-assistant.git
cd multi-agent-research-assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
```
langchain
langchain-groq
langgraph
streamlit
duckduckgo-search
trafilatura
readability-lxml
beautifulsoup4
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY_1=your_groq_key_1   # Agent 1 (Search)
GROQ_API_KEY_2=your_groq_key_2   # Agent 2 (Reader)
GROQ_API_KEY_3=your_groq_key_3   # Agent 3 (Writer)
GROQ_API_KEY_4=your_groq_key_4   # Agent 4 (Critic)
```

> Get free Groq API keys at [console.groq.com](https://console.groq.com) - no credit card required.

### 4. Run the Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`, enter any research topic, and click **Run**.

---

## 📁 Project Structure

```
multi-agent-research-assistant/
│
├── app.py                  # Streamlit frontend & pipeline runner
├── agents/
│   ├── search_agent.py     # Agent 1 - DuckDuckGo direct call
│   ├── reader_agent.py     # Agent 2 - LangGraph React scraper
│   ├── writer_agent.py     # Agent 3 - LangChain LCEL chain
│   └── critic_agent.py     # Agent 4 - LangChain LCEL chain
├── tools/
│   └── scraper.py          # 3-layer scraping tool (trafilatura → readability → BS4)
├── .env                    # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## 📚 References

- [LangChain Documentation](https://docs.langchain.com)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Groq Console](https://console.groq.com)
- [Meta LLaMA 3.3](https://llama.meta.com)
- [trafilatura](https://trafilatura.readthedocs.io)
- [Streamlit](https://streamlit.io)

---

<div align="center">

**Multi-Agent Research Assistant** - Agentic AI | Spring 2026  
FAST-NUCES Karachi · Department of Computer Science

*Built with ❤️ using open-source tools at $0.00/day*

</div>
