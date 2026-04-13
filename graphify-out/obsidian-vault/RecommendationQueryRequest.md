# RecommendationQueryRequest

- **Type:** code
- **Source:** `src\phase_2_retrieval\model_recommendation.py` L6
- **Community:** 3

## Outgoing
- `uses` → [[FilterState|FilterState]]
- `uses` → [[Copy for when we widen filters so results are not empty or too sparse.|Copy for when we widen filters so results are not empty or too sparse.]]
- `uses` → [[GroqChatClient|GroqChatClient]]
- `uses` → [[_FakeClient|_FakeClient]]

## Incoming
- [[Streamlit host for the restaurant recommender (deploy on Streamlit Community Clo|Streamlit host for the restaurant recommender (deploy on Streamlit Community Clo]] → `uses`
- [[BaseModel|BaseModel]] → `inherits`
- [[model_recommendation.py|model_recommendation.py]] → `contains`
