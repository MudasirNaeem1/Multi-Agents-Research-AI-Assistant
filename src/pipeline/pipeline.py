from src.agents.agents import run_search, build_reader_agent, get_writer_chain, get_critic_chain


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # ── Step 1 — Search (direct tool call, no LLM loop) ──────────────────────
    print("\n" + "=" * 50)
    print("Step 1 — Searching the web (direct) ...")
    print("=" * 50)

    state["search_results"] = run_search(topic)
    print("\n[Search Results]\n", state["search_results"])

    # ── Step 2 — Reader Agent ─────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("Step 2 — Reader Agent is scraping top resources ...")
    print("=" * 50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Here are search results for the topic: '{topic}'\n\n"
            f"Search Results:\n{state['search_results']}\n\n"
            f"Please scrape the top 3 URLs from these results to get detailed content."
        )]
    })
    state["scraped_content"] = reader_result["messages"][-1].content
    print("\n[Scraped Content]\n", state["scraped_content"])

    # ── Step 3 — Writer Chain ─────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("Step 3 — Writer is drafting the report ...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )
    writer_chain = get_writer_chain()
    state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
    print("\n[Final Report]\n", state["report"])

    # ── Step 4 — Critic Chain ─────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("Step 4 — Critic is reviewing the report ...")
    print("=" * 50)

    critic_chain = get_critic_chain()
    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    print("\n[Critic Feedback]\n", state["feedback"])

    return state