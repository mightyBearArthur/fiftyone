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
    Tuple,
    TypeVar,
    # overload,
)

from pymongo.cursor import Cursor as _Cursor

from fiftyone.core._pymongo_proxy.util import PymongoWSBase, PymongoProxyMeta

if TYPE_CHECKING:
    from fiftyone.core._pymongo_proxy.collection import Collection

_DocumentType = TypeVar("_DocumentType")


def _proxy_return_self(
    method_name: str,
    instance: "Cursor",
    *args,
    **kwargs,
) -> Any:
    instance.request(
        pymongo_attr_name=method_name,
        pymongo_args=args,
        pymongo_kwargs=kwargs,
    )
    return instance


class Cursor(
    PymongoWSBase,
    metaclass=PymongoProxyMeta,
    pymongo_cls=_Cursor,
    pymongo_method_proxy=_proxy_return_self,
):
    """Proxy class for pymongo.cursor.Cursor"""

    def __init__(
        self,
        collection: "Collection",
        *args: Any,
        __messages=None,
        **kwargs: Any,
    ):
        self._collection = collection
        super().__init__(*args, **kwargs)

        self._sent_messages = []
        if __messages:
            for msg in __messages:
                self._request(msg)
                self._sent_messages.append(msg)
        else:
            self.request()

    @property
    def api_endpoint_url(self) -> str:
        return os.path.join(
            self.collection.api_endpoint_url.replace("http", "ws"), "cursor"
        )

    @property
    def collection(self) -> "Collection[_DocumentType]":
        """The collection this cursor is bound to"""
        return self._collection

    def __copy__(self) -> "Cursor[_DocumentType]":
        return self.clone()

    def __deepcopy__(self, memo: Any) -> Any:
        return self.clone()

    @property
    def address(self) -> Optional[Tuple[str, Any]]:
        return None

    @property
    def session(self) -> None:
        return None

    def clone(self):
        """Clone the cursor"""
        return self.__class__(self._collection, __messages=self._sent_messages)

    def explain(self) -> _DocumentType:
        """Close the cursor"""
        # Overriding because default behavior is to proxy and return self
        return self.request(pymongo_attr_name="explain")

    def distinct(self, key: str) -> List:
        """Get distinct"""
        # Overriding because default behavior is to proxy and return self
        return self.request(pymongo_attr_name="distinct", pymongo_args=[key])

    def build_payload(  # pylint: disable=dangerous-default-value
        self,
        *,
        pymongo_attr_name: Optional[str] = None,
        pymongo_args: Optional[List[Any]] = [],
        pymongo_kwargs: Optional[Dict[str, Any]] = {},
    ) -> Dict[str, Any]:
        payload = self.collection.build_payload(
            pymongo_attr_name=pymongo_attr_name,
            pymongo_args=pymongo_args,
            pymongo_kwargs=pymongo_kwargs,
        )

        payload.update(
            crs_ar=self.serialize_for_request(self._init_args),
            crs_kw=self.serialize_for_request(self._init_kwargs),
        )

        return payload

    def _request(self, payload: dict[str, Any]) -> Any:
        return_value = super()._request(payload)
        self._sent_messages.append(payload)
        return return_value


class RawBatchCursor(
    Cursor,
    pymongo_cls=_Cursor,
    pymongo_method_proxy=_proxy_return_self,
):
    ...
