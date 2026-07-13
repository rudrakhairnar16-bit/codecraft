from __future__ import annotations

from collections.abc import Callable

from tree_sitter import Language, Parser, Query, QueryCursor

from codecraft.models.file import FileConcept
from codecraft.scanner.multilang.parser import BaseParser


class TreeSitterParser(BaseParser):
    LANGUAGE_FN: Callable[[], Language] | None = None
    QUERIES: list[tuple[str, str]] = []

    def __init__(self) -> None:
        assert self.LANGUAGE_FN is not None
        lang = Language(self.LANGUAGE_FN())
        self.parser = Parser(lang)
        self._queries = self._build_queries(lang)

    def _build_queries(self, lang: Language) -> list[tuple[Query, dict[str, str]]]:
        result = []
        chunk: list[tuple[str, str]] = []
        for pattern, concept in self.QUERIES:
            chunk.append((pattern, concept))
            if len(chunk) >= 10:
                result.append(self._compile_query(lang, chunk))
                chunk = []
        if chunk:
            result.append(self._compile_query(lang, chunk))
        return result

    def _compile_query(self, lang: Language, patterns: list[tuple[str, str]]) -> tuple[Query, dict[str, str]]:
        tags: list[str] = []
        tag_to_concept: dict[str, str] = {}
        for pattern, concept in patterns:
            tag = f"c{len(tags)}"
            tags.append(f"({pattern}) @{tag}")
            tag_to_concept[tag] = concept
        return Query(lang, " ".join(tags)), tag_to_concept

    def parse(self, source_code: str, file_path: str) -> dict[str, FileConcept]:
        concepts: dict[str, int] = {}
        try:
            tree = self.parser.parse(bytes(source_code, "utf-8"))
        except Exception:
            return {}
        for query, tag_map in self._queries:
            try:
                cursor = QueryCursor(query)
                captures = cursor.captures(tree.root_node)
                for tag, nodes in captures.items():
                    concept = tag_map.get(tag)
                    if concept:
                        concepts[concept] = concepts.get(concept, 0) + len(nodes)
            except Exception:
                continue
        return {
            name: FileConcept(concept_name=name, occurrences=count)
            for name, count in concepts.items()
        }
