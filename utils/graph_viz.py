from __future__ import annotations

import tempfile

import networkx as nx
from pyvis.network import Network


def render_knowledge_graph(user_skills: list[str], missing_skills: list[str], role_label: str) -> str:
    graph = nx.Graph()
    graph.add_node(role_label, group="role")

    for skill in user_skills[:15]:
        graph.add_node(skill, group="user")
        graph.add_edge(role_label, skill, relation="has")

    for skill in missing_skills[:15]:
        graph.add_node(skill, group="missing")
        graph.add_edge(role_label, skill, relation="requires")

    net = Network(height="500px", width="100%", bgcolor="#ffffff", font_color="#111111")
    net.from_nx(graph)

    for node in net.nodes:
        if node["id"] == role_label:
            node["color"] = "#1d4ed8"
            node["size"] = 35
        elif node["id"] in missing_skills:
            node["color"] = "#dc2626"
        else:
            node["color"] = "#16a34a"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        net.save_graph(tmp.name)
        with open(tmp.name, "r", encoding="utf-8") as html_file:
            return html_file.read()
