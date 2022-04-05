from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, List, Union, TYPE_CHECKING

from .common import ModelBase
from .pagination import PaginatedList, AsyncPaginatedList
from ..const import DEFAULT_PAGE_SIZE

if TYPE_CHECKING:
    from .accounts import Account
    from .transactions import TransactionStatus, AsyncTransaction, Transaction


class Tag(ModelBase):
    """Representation of a Tag."""

    id: str
    """The label of the tag, which also acts as the tags unique identifier."""

    def transactions(
        self,
        account: Union[str, Account] = None,
        *,
        status: TransactionStatus = None,
        since: datetime = None,
        until: datetime = None,
        category: Union[str, PartialCategory] = None,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[Transaction]:
        """Retrieves transactions for a specific account or all accounts.

        Arguments:
            account: An account/id to fetch transactions from.
                     If `None`, returns transactions across all accounts.
            status: The transaction status for which to return records.
            since: The start `datetime` from which to return records.
            until: The end `datetime` up to which to return records.
            category: The category/id identifier for which to filter transactions.
                      Raises exception for invalid category.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the transactions.
        """
        return self._client.transactions(
            account,
            status=status,
            since=since,
            until=until,
            category=category,
            tag=self,
            limit=limit,
            page_size=page_size,
        )

    def __repr__(self):
        return f"<Tag id='{self.id}'>"


class AsyncTag(Tag):
    async def transactions(
        self,
        account: Union[str, Account] = None,
        *,
        status: TransactionStatus = None,
        since: datetime = None,
        until: datetime = None,
        category: Union[str, PartialCategory] = None,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncPaginatedList[AsyncTransaction]:
        """Retrieves transactions for a specific account or all accounts.

        Arguments:
            account: An account/id to fetch transactions from.
                     If `None`, returns transactions across all accounts.
            status: The transaction status for which to return records.
            since: The start `datetime` from which to return records.
            until: The end `datetime` up to which to return records.
            category: The category/id identifier for which to filter transactions.
                      Raises exception for invalid category.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the transactions.
        """
        return await self._client.transactions(
            account,
            status=status,
            since=since,
            until=until,
            category=category,
            tag=self,
            limit=limit,
            page_size=page_size,
        )


class PartialCategory(ModelBase):
    """Representation of a PartialCategory."""

    id: str
    """The unique identifier for this category.

    This is a human-readable but URL-safe value.
    """

    def category(self) -> Category:
        """Returns the full category information for a partial category."""
        if isinstance(self, Category):
            return self
        return self._client.category(self.id)

    def transactions(
        self,
        account: Union[str, Account] = None,
        *,
        status: TransactionStatus = None,
        since: datetime = None,
        until: datetime = None,
        tag: Union[str, Tag] = None,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[Transaction]:
        """Retrieves transactions for a specific account or all accounts.

        Arguments:
            account: An account/id to fetch transactions from.
                     If `None`, returns transactions across all accounts.
            status: The transaction status for which to return records.
            since: The start `datetime` from which to return records.
            until: The end `datetime` up to which to return records.
            tag: A transaction tag/id to filter for which to return records.
                 Returns empty if tag does not exist.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the transactions.
        """
        return self._client.transactions(
            account,
            status=status,
            since=since,
            until=until,
            category=self,
            tag=tag,
            limit=limit,
            page_size=page_size,
        )

    def __repr__(self):
        return f"<PartialCategory id='{self.id}'>"


class AsyncPartialCategory(PartialCategory):
    async def category(self) -> Category:
        """Returns the full category information for a partial category."""
        if isinstance(self, Category):
            return self
        return await self._client.category(self.id)

    async def transactions(
        self,
        account: Union[str, Account] = None,
        *,
        status: TransactionStatus = None,
        since: datetime = None,
        until: datetime = None,
        tag: Union[str, Tag] = None,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncPaginatedList[AsyncTransaction]:
        """Retrieves transactions for a specific account or all accounts.

        Arguments:
            account: An account/id to fetch transactions from.
                     If `None`, returns transactions across all accounts.
            status: The transaction status for which to return records.
            since: The start `datetime` from which to return records.
            until: The end `datetime` up to which to return records.
            tag: A transaction tag/id to filter for which to return records.
                 Returns empty if tag does not exist.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the transactions.
        """
        return await self._client.transactions(
            account,
            status=status,
            since=since,
            until=until,
            category=self,
            tag=tag,
            limit=limit,
            page_size=page_size,
        )


class PartialCategoryParent(PartialCategory):
    """Representation of a PartialCategoryParent.

    This is used when an API response includes a partial category and a partial parent.
    """

    parent: Optional[PartialCategory] = None
    """The parent category of this category, if it exists."""

    def __parse__(self, attrs: Dict, relations: Dict, links: Optional[Dict]):
        if relations["parent"]["data"]:
            self.parent = PartialCategory(self._client, relations["parent"])

    def __repr__(self):
        if self.parent:
            return f"<PartialCategoryParent id='{self.id}' parent='{self.parent.id}'>"
        return f"<PartialCategoryParent id='{self.id}'>"


class AsyncPartialCategoryParent(PartialCategoryParent, AsyncPartialCategory):
    parent: Optional[AsyncPartialCategory] = None


class Category(PartialCategoryParent):
    """Representation of a Category."""

    name: str
    """The name of this category as seen in the Up application."""

    children: List[PartialCategory]
    """The subcategories of this category."""

    def __parse__(self, attrs: Dict, relations: Dict, links: Optional[Dict]):
        super().__parse__(attrs, relations, links)
        self.name = attrs["name"]
        self.children = [
            PartialCategory(self._client, x) for x in relations["children"]["data"]
        ]

    def __repr__(self):
        if self.parent:
            return f"<Category '{self.name}': id='{self.id}' parent='{self.parent.id}'>"
        return f"<Category '{self.name}': id='{self.id}'>"


class AsyncCategory(Category, AsyncPartialCategory):
    children: List[AsyncPartialCategory]
