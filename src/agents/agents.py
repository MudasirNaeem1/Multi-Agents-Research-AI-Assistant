from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv()

# ── Groq client factory ───────────────────────────────────────────────────────

def _groq(key_env: str) -> ChatGroq:
    api_key = os.getenv(key_env)
    if not api_key:
        raise ValueError(f"Environment variable '{key_env}' is not set.")
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=api_key,
        model_kwargs={"tool_choice": "auto"},
    )


# ── Agent 1 — Search (DIRECT TOOL CALL — no ReAct loop) ──────────────────────
# WHY: create_react_agent makes LLaMA think→act→observe→think in a loop.
# On Groq free tier this takes 60-120s just for a search.
# Search only ever needs ONE tool call, so we skip the LLM entirely.

def run_search(topic: str) -> str:
    """Directly calls the web_search tool. No LLM, no loop. Instant."""
    return web_search.invoke({"query": topic})


# ── Agent 2 — Reader Agent (GROQ_API_KEY_2) ──────────────────────────────────

def build_reader_agent():
    llm = _groq("GROQ_API_KEY_2")
    system_prompt = (
        "You are a web content extractor. "
        "You will receive a list of search results with URLs. "
        "Your job is to scrape the top 3 URLs using the scrape_url tool — one at a time. "
        "Do NOT judge relevance by the website name or URL structure. "
        "Any URL that is not a social media post, login page, or PDF is worth scraping. "
        "After scraping each URL, combine all extracted content and return it. "
        "Always include the source URL with each piece of scraped content."
    )
    return create_react_agent(llm, [scrape_url], prompt=system_prompt)


# ── Agent 3 — Writer Chain (GROQ_API_KEY_3) ──────────────────────────────────

writer_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert research writer. "
     "You MUST write your report using ONLY the information provided in the research below. "
     "Do NOT use your own knowledge, do NOT invent facts, statistics, or quotes. "
     "If the research is limited, say so honestly rather than filling gaps with assumptions. "
     "Write in a clear, structured, professional tone."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report exactly as:

## Introduction
[Brief overview based strictly on the research provided]

## Key Findings
[Minimum 3 well-explained points — each must be grounded in the research above]

## Conclusion
[Summary and takeaways based on the research]

## Sources
[List every URL that appears anywhere in the research above, one per line, with the page title if available]

Important: Only write what the research supports. If a point is not in the research, do not include it."""),
])

def get_writer_chain():
    llm = _groq("GROQ_API_KEY_3")
    return writer_prompt | llm | StrOutputParser()


# ── Agent 4 — Critic Chain (GROQ_API_KEY_4) ──────────────────────────────────

critic_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a fair and constructive research critic. "
     "Reward good content, structure, relevance, and proper sourcing. "
     "Only deduct points for genuinely missing, unsupported, or incorrect information. "
     "Pay special attention to whether the sources section contains real URLs."),
    ("human", """Review the research report below and evaluate it.

Report:
{report}

Scoring guide:
- 9-10: Well structured, relevant, covers key points, has real source URLs
- 7-8: Good content but missing some depth or has few/no sources
- 5-6: Relevant but poorly structured, thin content, or no sources at all
- Below 5: Only if content is completely irrelevant, fabricated, or wrong

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

def get_critic_chain():
    llm = _groq("GROQ_API_KEY_4")
    return critic_prompt | llm | StrOutputParser()