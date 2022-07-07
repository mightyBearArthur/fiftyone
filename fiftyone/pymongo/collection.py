"""
| Copyright 2017-2022, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
)

from pymongo.collection import Collection as _Collection

from fiftyone.pymongo.cursor import Cursor
from fiftyone.pymongo.util import (
    PymongoAPIBase,
    PymongoProxyMeta,
    with_doc_and_sig,
)

if TYPE_CHECKING:
    from fiftyone.pymongo.database import Database


def _proxy(
    method_name: str,
    instance: "Collection",
    *args,
    **kwargs,
) -> Any:
    return instance.request(
        pymongo_method_name=method_name,
        pymongo_args=args,
        pymongo_kwargs=kwargs,
    )


class Collection(
    PymongoAPIBase,
    metaclass=PymongoProxyMeta,
    pymongo_cls=_Collection,
    pymongo_method_proxy=_proxy,
):
    """Proxy class for pymongo.collection.Collection"""

    def __init__(self, database: "Database", name: str):
        self._database = database
        self._name = name

    @property
    def api_endpoint_url(self) -> str:
        return self.database.api_endpoint_url

    @property
    def name(self) -> str:
        """The name of this collection"""
        return self._name

    @property
    def database(self) -> "Database":
        """The database this collection belongs to"""
        return self._database

    @with_doc_and_sig(_Collection.find)
    def find(self, *args, **kwargs):  # pylint: disable=missing-docstring
        return Cursor(self, *args, **kwargs)

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
            database=self.database.name,
            collection=self.name,
        )

        return payload
