"""
| Copyright 2017-2022, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pymongo.database import Database as _Database

from fiftyone.pymongo.collection import Collection
from fiftyone.pymongo.util import (
    PymongoAPIBase,
    PymongoProxyMeta,
    with_doc_and_sig,
)

if TYPE_CHECKING:
    from fiftyone.pymongo.client import Client


def _proxy(
    method_name: str,
    instance: "Database",
    *args,
    **kwargs,
) -> Any:
    return instance.request(
        pymongo_method_name=method_name,
        pymongo_args=args,
        pymongo_kwargs=kwargs,
    )


# TODO: look into the following:
# database.fs.files.distinct("_id", {}, {}) ????
# database.fs.files.delete_many({"_id": {"$in": result_ids}})
# database.fs.chunks.delete_many({"files_id": {"$in": result_ids}})


class Database(
    PymongoAPIBase,
    metaclass=PymongoProxyMeta,
    pymongo_cls=_Database,
    pymongo_method_proxy=_proxy,
):
    """Proxy class for pymongo.database.Database"""

    def __init__(self, client: "Client", name: str):
        self._client = client
        self._name = name
        self._collection_cache = {}

    # TODO: add attribute access to collections
    # def __getattribute__(self, __name: str, /) -> Any:
    #     ...

    def __getitem__(self, __k: str, /) -> Collection:
        return self.get_collection(__k)

    @with_doc_and_sig(_Database.find)
    def get_collection(  # pylint: disable=missing-docstring
        self, collection_name: str
    ) -> Collection:
        if collection_name not in self._collection_cache:
            self._collection_cache[collection_name] = Collection(
                self, collection_name
            )
        return self._collection_cache[collection_name]

    @property
    def client(self) -> "Client":
        """The client bound to this database"""
        return self._client

    @property
    def api_endpoint_url(self) -> str:
        return self.client.api_endpoint_url

    @property
    def name(self) -> str:
        """The name of this database"""
        return self._name

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
            database=self.name,
        )

        return payload
