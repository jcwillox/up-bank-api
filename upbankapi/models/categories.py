from typing import Optional, Dict, List

from .common import ModelBase


class Tag(ModelBase):
    """Representation of a Tag."""

    id: str
    """The label of the tag, which also acts as the tags unique identifier."""

    def __repr__(self):
        return f"<Tag id='{self.id}'>"


class PartialCategory(ModelBase):
    """Representation of a PartialCategory."""

    id: str
    """The unique identifier for this category.

    This is a human-readable but URL-safe value.
    """

    def __repr__(self):
        return f"<PartialCategory id='{self.id}'>"


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
