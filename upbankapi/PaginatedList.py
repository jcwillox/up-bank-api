from typing import TYPE_CHECKING, Generic, List, Iterator, Union, TypeVar, Any

from .const import BASE_URL
from .models import ModelBase

if TYPE_CHECKING:
    from .client import Client

T = TypeVar("T", bound=ModelBase)


class PaginatedList(Generic[T]):
    def __init__(
        self, client: "Client", content_class, elements: List, next_url: str, limit: int
    ):
        self._elements = elements
        self._client = client
        self._content_class = content_class
        self._limit = limit
        self._next_url = next_url

    def __getitem__(self, index: Union[int, slice]) -> Any:  # -> Union[T, "_Slice"]:
        assert isinstance(index, (int, slice))
        if isinstance(index, int):
            self._fetch_to(index)
            return self._elements[index]
        return self._Slice(self, index)

    def __iter__(self) -> Iterator[T]:
        for element in self._elements:
            yield element
        while self.has_next:
            new_elements = self.next()
            for element in new_elements:
                yield element

    @property
    def count(self):
        return len(self._elements)

    @property
    def has_next(self) -> bool:
        if not self._next_url:
            return False
        if self._limit:
            return self.count < self._limit
        return True

    def _fetch_to(self, index):
        while len(self._elements) <= index and self.has_next:
            self.next()

    def next(self) -> List[T]:
        response = self._client.api(self._next_url.replace(BASE_URL, ""))
        self._next_url = response["links"].get("next")
        new_elements = [
            self._content_class(self._client, item) for item in response["data"]
        ]

        if self._limit:
            diff = self.count + len(new_elements) - self._limit
            if diff > 0:
                new_elements = new_elements[: diff - 1]

        self._elements += new_elements
        return new_elements

    class _Slice:
        def __init__(self, _list: "PaginatedList[T]", _slice: slice):
            self.__list = _list
            self.__start = _slice.start or 0
            self.__end = _slice.stop
            self.__step = _slice.step or 1

        def __iter__(self) -> Iterator[T]:
            index = self.__start
            while self.__end and index < self.__end:
                if self.__list.count > index or self.__list.has_next:
                    yield self.__list[index]
                    index += self.__step
                else:
                    return
