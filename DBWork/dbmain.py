from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Purchase:
    date: str
    product: str
    desc: str
    cost: float
    sum_: float
    id_: int = 0


@dataclass
class Category:
    category: str
    product: str
    hint: str


class DBWork(ABC):

    # ==============================================================
    # Select data
    # ==============================================================

    @abstractmethod
    async def select_purchase_item(self, id_: int) -> Purchase | None:
        pass

    @abstractmethod
    async def select_all_purchases(self) -> list[Purchase]:
        pass

    @abstractmethod
    async def select_all_categories(self) -> list[Category]:
        pass

    @abstractmethod
    async def select_category_by_product(self, product: str) -> Category | None:
        pass

    # ==============================================================
    # Insert Delete Update
    # ==============================================================

    @abstractmethod
    async def insert_into_purchases(self, purchase: Purchase) -> None:
        pass

    @abstractmethod
    async def delete_from_purchases(self, id_: int) -> None:
        pass

    @abstractmethod
    async def update_purchases(self, purchase: Purchase) -> None:
        pass

    @abstractmethod
    async def insert_into_categories(self, category: Category) -> None:
        pass
