from __future__ import annotations

from codecraft.db.repository import Repository
from codecraft.models.challenge import Challenge, ChallengeType
from codecraft.models.debt import DebtItem, DebtReport


class DebtTrackerEngine:
    def __init__(self, repo: Repository):
        self.repo = repo

    def scan_and_track(self, debt_items: list[DebtItem]) -> DebtReport:
        report = DebtReport()

        for item in debt_items:
            existing = self.repo.get_unresolved_debt()
            is_duplicate = any(
                e.pattern_type == item.pattern_type
                and e.file_path == item.file_path
                for e in existing
            )
            if not is_duplicate:
                self.repo.insert_debt_item(item)
                report.total_items += 1

        all_items = self.repo.get_all_debt_items()
        report.total_items = len(all_items)
        report.resolved_items = sum(1 for i in all_items if i.resolved)
        report.items = all_items

        by_type: dict[str, int] = {}
        for item in all_items:
            if not item.resolved:
                by_type[item.pattern_type] = by_type.get(item.pattern_type, 0) + 1
        report.by_type = by_type

        report.score = self._compute_score(all_items)
        return report

    def _compute_score(self, items: list[DebtItem]) -> float:
        if not items:
            return 0.0
        unresolved = [i for i in items if not i.resolved]
        total_weight = sum(i.difficulty for i in items)
        unresolved_weight = sum(i.difficulty for i in unresolved)
        if total_weight == 0:
            return 1.0
        return 1.0 - (unresolved_weight / total_weight)

    def get_report(self) -> DebtReport:
        all_items = self.repo.get_all_debt_items()
        unresolved = self.repo.get_unresolved_debt()
        by_type: dict[str, int] = {}
        for item in unresolved:
            by_type[item.pattern_type] = by_type.get(item.pattern_type, 0) + 1

        return DebtReport(
            total_items=len(all_items),
            resolved_items=sum(1 for i in all_items if i.resolved),
            by_type=by_type,
            items=unresolved,
            score=self._compute_score(all_items),
        )

    def generate_challenge(self, debt_item: DebtItem) -> Challenge:
        assert debt_item.file_path is not None
        challenge_id = f"debt_{debt_item.pattern_type}_{debt_item.file_path.stem}"

        alt_lines = debt_item.alternative_code.split("\n")
        hint_lines = []
        for line in alt_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                hint_lines.append(line)

        num_hints = len(hint_lines)
        hints = []
        for i in range(min(num_hints, 3)):
            hints.append(f"Hint {i+1}: Try using this approach — {hint_lines[i]}")

        return Challenge(
            id=challenge_id,
            challenge_type=ChallengeType.REFACTOR,
            concept_name=debt_item.pattern_type,
            title=f"Refactor: {debt_item.pattern_type.replace('_', ' ').title()}",
            description=debt_item.suggestion,
            code_snippet=debt_item.old_snippet,
            expected_solution=debt_item.alternative_code,
            hints=hints,
            difficulty=debt_item.difficulty,
            source_file=str(debt_item.file_path),
        )

    def resolve(self, item_id: int) -> None:
        self.repo.resolve_debt_item(item_id)
