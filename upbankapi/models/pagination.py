from typing import (
    TYPE_CHECKING,
    Generic,
    List,
    Iterator,
    Union,
    TypeVar,
    Type,
    AsyncIterator,
    Dict,
    Optional,
    Any,
    Coroutine,
    cast,
)

from .common import ModelBase
from ..const import BASE_URL

if TYPE_CHECKING:
    from ..client import Client, AsyncClient

T = TypeVar("T", bound=ModelBase)


class PaginatedList(Generic[T]):
    _client: "Client"
    _next_url: Optional[str] = None
    _elements: List[T]
    _limit: int

    def __init__(
        self,
        client: "Client",
        cls: Type[ModelBase],
        data: Dict,
        limit: int,
    ):
        self._elements = [cls(client, x) for x in data["data"]]
        self._client = client
        self._limit = limit
        self._cls = cls

        if data["links"]["next"]:
            self._next_url: Optional[str] = data["links"]["next"][len(BASE_URL) :]

    def __getitem__(self, index: Union[int, slice]) -> Union[T, "PaginatedList._Slice"]:
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

    def __len__(self):
        return len(self._elements)

    @property
    def has_next(self) -> bool:
        if not self._next_url:
            return False
        if self._limit:
            return len(self._elements) < self._limit
        return True

    def _fetch_to(self, index):
        while len(self._elements) <= index and self.has_next:
            self.next()

    def next(self) -> List[T]:
        # next_url is not none for this to be called
        return self._handle_next(self._client.api(self._next_url))

    def _handle_next(self, data: Dict):
        self._next_url = data["links"]["next"]
        if self._next_url:
            self._next_url = self._next_url[len(BASE_URL) :]

        new_elements = [self._cls(self._client, item) for item in data["data"]]

        # ensure we don't return more elements than the limit
        if self._limit:
            diff = len(self._elements) + len(new_elements) - self._limit
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
                if len(self.__list) > index or self.__list.has_next:
                    yield self.__list[index]
                    index += self.__step
                else:
                    return


class AsyncPaginatedList(PaginatedList[T]):
    _client: "AsyncClient"

    def __init__(
        self, client: "AsyncClient", cls: Type[ModelBase], data: Dict, limit: int
    ):
        super().__init__(cast(Any, client), cls, data, limit)

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[Coroutine[Any, Any, T], "AsyncPaginatedList._AsyncSlice"]:
        if isinstance(index, int):
            return self.__get_index(index)
        return AsyncPaginatedList._AsyncSlice(self, index)

    async def __get_index(self, index: int) -> T:
        await self._fetch_to(index)
        return self._elements[index]

    def __iter__(self):
        raise NotImplementedError("must be used with `async for`")

    async def __aiter__(self) -> AsyncIterator[T]:
        for element in self._elements:
            yield element
        while self.has_next:
            new_elements = await self.next()
            for element in new_elements:
                yield element

    async def _fetch_to(self, index):
        while len(self._elements) <= index and self.has_next:
            await self.next()

    async def next(self) -> List[T]:
        return self._handle_next(await self._client.api(self._next_url))

    class _AsyncSlice:
        def __init__(self, _list: "AsyncPaginatedList[T]", _slice: slice):
            self.__list = _list
            self.__start = _slice.start or 0
            self.__end = _slice.stop
            self.__step = _slice.step or 1

        async def __aiter__(self) -> AsyncIterator[T]:
            index = self.__start
            while self.__end and index < self.__end:
                if len(self.__list) > index or self.__list.has_next:
                    yield await self.__list[index]
                    index += self.__step
                else:
                    return
