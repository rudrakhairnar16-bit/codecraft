from __future__ import annotations

from abc import ABC, abstractmethod

from codecraft.models.file import FileConcept


class BaseParser(ABC):
    @abstractmethod
    def parse(self, source_code: str, file_path: str) -> dict[str, FileConcept]:
        ...
