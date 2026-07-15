from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from codecraft.db.repos.card_repo import CardRepo
from codecraft.db.repos.challenge_repo import ChallengeRepo
from codecraft.db.repos.concept_repo import ConceptRepo
from codecraft.db.repos.debt_repo import DebtRepo
from codecraft.db.repos.file_repo import FileRepo
from codecraft.db.repos.settings_repo import SettingsRepo
from codecraft.models.challenge import ChallengeResult
from codecraft.models.debt import DebtItem
from codecraft.models.file import FileConcept, FileRecord
from codecraft.models.review import SpacedRepetitionCard


class Repository:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn
        self.files = FileRepo(conn)
        self.concepts = ConceptRepo(conn)
        self.debt = DebtRepo(conn)
        self.cards = CardRepo(conn)
        self.settings = SettingsRepo(conn)
        self.challenges = ChallengeRepo(conn)

    def upsert_file(self, record: FileRecord) -> None:
        self.files.upsert(record)

    def get_file(self, path: Path) -> FileRecord | None:
        return self.files.get(path)

    def get_all_files(self) -> list[FileRecord]:
        return self.files.get_all()

    def upsert_file_concepts(
        self, file_path: Path, concepts: dict[str, FileConcept]
    ) -> None:
        self.concepts.upsert_file_concepts(file_path, concepts)

    def get_file_concepts(self, file_path: Path) -> dict[str, FileConcept]:
        return self.concepts.get_file_concepts(file_path)

    def get_all_concept_names(self) -> list[str]:
        return self.concepts.get_all_names()

    def get_last_usage(self, concept_name: str) -> Any:
        return self.concepts.get_last_usage(concept_name)

    def get_exposure_count(self, concept_name: str) -> int:
        return self.concepts.get_exposure_count(concept_name)

    def get_concept_timeline(self, concept_name: str) -> list[dict[str, Any]]:
        return self.concepts.get_timeline(concept_name)

    def insert_debt_item(self, item: DebtItem) -> None:
        self.debt.insert(item)

    def resolve_debt_item(self, item_id: int) -> None:
        self.debt.resolve(item_id)

    def get_unresolved_debt(self) -> list[DebtItem]:
        return self.debt.get_unresolved()

    def get_all_debt_items(self) -> list[DebtItem]:
        return self.debt.get_all()

    def insert_challenge_result(self, result: ChallengeResult) -> None:
        self.challenges.insert(result)

    def get_challenge_history(
        self, concept_name: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        return self.challenges.get_history(concept_name, limit)

    def get_practice_stats(self) -> dict[str, Any]:
        return self.challenges.get_stats()

    def get_streak_data(self) -> dict[str, Any]:
        return self.challenges.get_streak()

    def upsert_card(self, card: SpacedRepetitionCard) -> None:
        self.cards.upsert(card)

    def get_card(self, concept_name: str) -> SpacedRepetitionCard | None:
        return self.cards.get(concept_name)

    def get_all_cards(self) -> list[SpacedRepetitionCard]:
        return self.cards.get_all()

    def get_setting(self, key: str, default: str = "") -> str:
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: str) -> None:
        self.settings.set(key, value)
