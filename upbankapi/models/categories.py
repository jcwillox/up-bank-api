from typing import Optional, Dict, List

from .common import ModelBase


class Tag(ModelBase):
    """Representation of a Tag."""

    id: str
    """The label of the tag, which also acts as the tags unique identifier."""

    def __str__(self):
        return self.id


class PartialCategory(ModelBase):
    """Representation of a PartialCategory."""

    id: str
    """The unique identifier for this category.

    This is a human-readable but URL-safe value.
    """

    def __str__(self):
        return self.id


class PartialCategoryParent(PartialCategory):
    """Representation of a PartialCategoryParent.

    This is used when an API response includes a partial category and a partial parent.
    """

    parent: Optional[PartialCategory]
    """The parent category of this category, if it exists."""

    def __parse__(self, attrs: Dict, relations: Dict, links: Optional[Dict]):
        if relations["parent"]["data"]:
            self.parent = PartialCategory(self._client, relations["parent"]["data"])


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

    def __str__(self):
        return self.name
