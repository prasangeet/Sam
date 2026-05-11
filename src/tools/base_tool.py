from abc import ABC, abstractmethod


class BaseTool(ABC):
    name = "base"

    @abstractmethod
    def execute(self, params: dict) -> str:
        pass
