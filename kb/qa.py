"""Q&A contra a wiki."""

from pathlib import Path
from kb.client import chat
from kb.config import WIKI_DIR
from kb.search import find_relevant


SYSTEM = """Você é um assistente de knowledge base. Responda perguntas com base nos artigos fornecidos.
- Cite os artigos que embasaram a resposta usando [[wikilink]]
- Se a informação não estiver nos artigos, diga explicitamente
- Seja direto e preciso
"""


def answer(question: str, top_k: int = 5) -> str:
    relevant = find_relevant(question, top_k=top_k)

    if not relevant:
        return "Nenhum artigo relevante encontrado na wiki. Use `kb compile` para adicionar conteúdo."

    context = "\n\n---\n\n".join(
        f"# {p.stem}\n{p.read_text(encoding='utf-8')}" for p in relevant
    )

    return chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Artigos relevantes:\n\n{context}\n\nPergunta: {question}"},
        ]
    )
