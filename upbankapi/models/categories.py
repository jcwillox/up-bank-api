from typing import Optional, Dict, List

from .common import ModelBase


class Tag(ModelBase):
    """Representation of a Tag"""

    # The label of the tag, which also acts as the tag’s unique identifier.
    id: str

    def __str__(self):
        return self.id


class PartialCategory(ModelBase):
    """Representation of a PartialCategory"""

    # The unique identifier for this category. This is a human-readable but URL-safe value.
    id: str

    def __str__(self):
        return self.id


class PartialCategoryParent(PartialCategory):
    """Representation of a PartialCategoryParent"""

    # The parent category of this category, if it exists.
    parent: Optional[PartialCategory]

    def __parse__(self, attrs: Dict, relations: Dict, **kwargs):
        if relations["parent"]["data"]:
            self.parent = PartialCategory(self._client, relations["parent"]["data"])


class Category(PartialCategoryParent):
    """Representation of a Category"""

    # The name of this category as seen in the Up application.
    name: str

    # The subcategories of this category.
    children: List[PartialCategory]

    def __parse__(self, attrs: Dict, relations: Dict, **kwargs):
        super().__parse__(attrs, relations, **kwargs)
        self.name = attrs["name"]
        self.children = [
            PartialCategory(self._client, x) for x in relations["children"]["data"]
        ]

    def __str__(self):
        return self.name
