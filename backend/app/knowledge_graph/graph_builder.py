import json
import re
from sqlalchemy.orm import Session
from app.agents.registry import get_agent
from app.models.knowledge_graph import KnowledgeNode, KnowledgeEdge

_EXTRACTION_PROMPT = (
    "You are extracting a knowledge graph. From the text below, extract entities and "
    "relationships. Entity types: user, project, topic, task, agent, document, technology, "
    "company, person. Respond with ONLY JSON, no prose:\n"
    '{"nodes": [{"label": "...", "type": "technology"}], '
    '"edges": [{"source": "...", "target": "...", "relation": "uses"}]}\n\n'
    "TEXT:\n{text}"
)


async def extract_and_store(db: Session, text: str) -> dict:
    """Uses the Reasoning Agent to pull entities/relations out of text, then upserts into the graph tables."""
    agent = get_agent("reasoning_agent")
    output = await agent.run(_EXTRACTION_PROMPT.format(text=text[:4000]), {})
    cleaned = re.sub(r"```json|```", "", output.raw).strip()

    try:
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {"nodes": [], "edges": []}

    label_to_id = {}
    for n in parsed.get("nodes", []):
        label = n.get("label", "").strip()
        if not label:
            continue
        existing = db.query(KnowledgeNode).filter(KnowledgeNode.label == label).first()
        if existing:
            label_to_id[label] = existing.id
            continue
        node = KnowledgeNode(label=label, node_type=n.get("type", "topic"))
        db.add(node)
        db.commit()
        db.refresh(node)
        label_to_id[label] = node.id

    for e in parsed.get("edges", []):
        src, tgt = e.get("source"), e.get("target")
        if src in label_to_id and tgt in label_to_id:
            db.add(KnowledgeEdge(
                source_id=label_to_id[src], target_id=label_to_id[tgt],
                relation=e.get("relation", "related_to"),
            ))
    db.commit()

    return {"nodes_created": len(label_to_id), "edges_created": len(parsed.get("edges", []))}


def get_graph(db: Session) -> dict:
    nodes = db.query(KnowledgeNode).all()
    edges = db.query(KnowledgeEdge).all()
    return {
        "nodes": [{"id": n.id, "label": n.label, "type": n.node_type} for n in nodes],
        "edges": [{"source": e.source_id, "target": e.target_id, "relation": e.relation} for e in edges],
    }
