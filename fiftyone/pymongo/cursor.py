"""
| Copyright 2017-2022, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import os
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    TypeVar,
    overload,
)

from pymongo.cursor import Cursor as _Cursor
import websocket

from fiftyone.pymongo.util import PymongoAPIBase, PymongoProxyMeta

if TYPE_CHECKING:
    from fiftyone.pymongo.collection import Collection

_DocumentType = TypeVar("_DocumentType")


def _proxy(
    method_name: str,
    instance: "Cursor",
    *args,
    **kwargs,
) -> Any:
    instance.request(
        pymongo_method_name=method_name,
        pymongo_args=args,
        pymongo_kwargs=kwargs,
    )
    return instance


class Cursor(
    PymongoAPIBase,
    metaclass=PymongoProxyMeta,
    pymongo_cls=_Cursor,
    pymongo_method_proxy=_proxy,
):
    """Proxy class for pymongo.cursor.Cursor"""

    def __init__(
        self,
        collection: "Collection",
        *args: Any,
        clone_from: Optional[str] = None,
        **kwargs: Any,
    ):
        self._collection = collection

        self._closed = False

        if clone_from:
            # TODO: implement
            ...

        self._ws = websocket.create_connection(self.api_endpoint_url)
        self.request(pymongo_args=args, pymongo_kwargs=kwargs)

    @property
    def api_endpoint_url(self) -> str:
        return os.path.join(
            self.collection.api_endpoint_url.replace("http", "ws"), "cursor"
        )

    @property
    def collection(self) -> "Collection[_DocumentType]":
        """The collection this cursor is bound to"""
        return self._collection

    def _request(self, payload: str) -> Any:
        self._ws.send(payload)
        return self._ws.recv()

    def next(self) -> _DocumentType:
        """Advance the cursor."""
        # TODO: potential for optimization
        return_value = self.request(pymongo_method_name="next")
        if return_value is None:
            raise StopIteration

    __next__ = next

    def __iter__(self):
        return self

    def __enter__(self) -> "Cursor[_DocumentType]":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:  # pylint: disable=broad-except
            ...

    # def __copy__(self) -> "Cursor[_DocumentType]":
    #     """Support function for `copy.copy()`.
    #     .. versionadded:: 2.4
    #     """
    #     return self._clone(deepcopy=False)

    # def __deepcopy__(self, memo: Any) -> Any:
    #     """Support function for `copy.deepcopy()`.
    #     .. versionadded:: 2.4
    #     """
    #     return self._clone(deepcopy=True)

    @overload
    def __getitem__(self, index: int) -> _DocumentType:
        ...

    @overload
    def __getitem__(self, index: slice) -> "Cursor[_DocumentType]":
        ...

    def __getitem__(self, index):
        return self.request(
            pymongo_method_name="__getitem__",
            pymongo_args=[index],
        )

    # @property
    # def address(self) -> Optional[Tuple[str, Any]]:
    #     return None

    # @property
    # def alive(self) -> bool:
    #     return self._closed

    # @property
    # def cursor_id(self) -> Optional[int]:
    #     return None

    # @property
    # def retrieved(self) -> int:
    #     # TODO: implement
    #     ...

    # @property
    # def session(self) -> None:
    #     return None

    def close(self):
        """Close the cursor"""
        if not self._closed:
            self._ws.close()
        self._closed = True

    # def clone(self):
    #     """Clone the cursor"""
    #     return self.__class__(self._collection, clone_from=self._id)

    def explain(self) -> _DocumentType:
        """Close the cursor"""
        return self.request(pymongo_method_name="explain")

    def distinct(self, key: str) -> List:
        """Get distinct"""
        return self.request(pymongo_method_name="distinct", pymongo_args=[key])

    def _build_payload(  # pylint: disable=dangerous-default-value
        self,
        pymongo_method_name: Optional[str] = None,
        pymongo_args: Optional[List[Any]] = [],
        pymongo_kwargs: Optional[Dict[str, Any]] = {},
    ) -> Dict[str, Any]:
        payload = super()._build_payload(
            pymongo_method_name,
            pymongo_args,
            pymongo_kwargs,
        )

        payload.update(
            database=self.collection.database.name,
            collection=self.collection.name,
        )
        return payload
