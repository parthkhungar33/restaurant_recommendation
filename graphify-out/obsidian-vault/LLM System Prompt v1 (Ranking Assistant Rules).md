# LLM System Prompt v1 (Ranking Assistant Rules)

- **Type:** document
- **Source:** `src/phase_3_llm/prompts/system_v1.txt` None
- **Community:** 0

## Outgoing
- `implements` → [[LLM Output JSON Schema (recommendations array)|LLM Output JSON Schema (recommendations array)]]
- `implements` → [[Hallucination Prevention Rule (Use Only Provided Candidates)|Hallucination Prevention Rule (Use Only Provided Candidates)]]
- `implements` → [[Explanation Tone Style Rules (Natural, Style-Aware)|Explanation Tone Style Rules (Natural, Style-Aware)]]
- `implements` → [[No Duplicate Restaurants Rule in Prompt|No Duplicate Restaurants Rule in Prompt]]

## Incoming
- [[Prompt Architecture (System + User + Candidate Context)|Prompt Architecture (System + User + Candidate Context)]] → `implements`
- [[TrackLog Step 8_ Phase 3 LLM Ranking Implementation|TrackLog Step 8: Phase 3 LLM Ranking Implementation]] → `references`
- [[src_phase_3_llm_ Groq LLM Ranking, Prompts, Fallback|src/phase_3_llm: Groq LLM Ranking, Prompts, Fallback]] → `references`
