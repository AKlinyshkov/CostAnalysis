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
    id_: int = 0


class DBWork(ABC):

    # ==============================================================
    # Work with purchases count
    # ==============================================================

    @property
    @abstractmethod
    def pur_count(self) -> int:
        pass

    @pur_count.setter
    @abstractmethod
    def pur_count(self, value):
        pass

    # ==============================================================
    # Select data
    # ==============================================================

    # ========================= Purchase ============================

    @abstractmethod
    async def select_purchase_item(self, id_: int) -> Purchase | None:
        pass

    @abstractmethod
    async def select_all_purchases(self) -> list[Purchase]:
        pass

    @abstractmethod
    async def select_page_purchases(self, page_num: int, row_per_page: int) -> list[Purchase]:
        pass

    # ========================= Category ============================

    @abstractmethod
    async def select_all_categories(self) -> list[Category]:
        pass

    @abstractmethod
    async def select_category_by_product(self, product: str) -> Category | None:
        pass

    @abstractmethod
    async def select_page_categories(self, page_num: int, row_per_page: int) -> list[Category] | None:
        pass

    # ==============================================================
    # Insert Delete Update
    # ==============================================================

    # ========================= Purchase ============================

    @abstractmethod
    async def insert_into_purchases(self, purchase: Purchase) -> None:
        pass

    @abstractmethod
    async def delete_from_purchases(self, id_: int) -> None:
        pass

    @abstractmethod
    async def update_purchases(self, purchase: Purchase) -> None:
        pass

    # ========================= Category ============================

    @abstractmethod
    async def insert_into_categories(self, category: Category) -> None:
        pass

    async def update_categories(self, category: Category) -> None:
        pass

    async def delete_from_categories(self, id_: int) -> None:
        pass

    # ==============================================================
    # Auxilliary
    # ==============================================================

    # List all categories
    async def get_list_categories(self) -> list[str] | None:
        pass

    # List all products of specified category (work with table Categories)
    async def select_product_by_category(self, category) -> list[str] | None:
        pass

    # Returns count of specified category purchases 
    async def select_count_specified_purchases(self, product: str) -> int | None:
        pass

    # Returns purchases of specified category
    async def select_specified_purchases(self, product: str, page_num: int, row_per_page: int) -> list[Purchase]:
        pass
