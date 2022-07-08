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
from pymongo.aggregation import (
    _CollectionAggregationCommand,
    _CollectionRawAggregationCommand,
)
from pymongo.collection import Collection as _Collection

from fiftyone.pymongo.change_stream import CollectionChangeStream
from fiftyone.pymongo.command_cursor import (
    CommandCursor,
    RawBatchCommandCursor,
)
from fiftyone.pymongo.cursor import Cursor, RawBatchCursor

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
        pymongo_attr_name=method_name,
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

    def __init__(
        self,
        database: "Database",
        name: str,
        /,
        *init_args,
        **init_kwargs,
    ):
        self._database = database
        self._name = name
        self._init_args = init_args
        self._init_kwargs = init_kwargs

    @property
    def api_endpoint_url(self) -> str:
        return self.database.api_endpoint_url

    # c[name] || c.name

    # Get the name sub-collection of Collection c.

    # Raises InvalidName if an invalid collection name is used.

    @property
    def name(self) -> str:
        """The name of this Collection."""
        return self._name

    @property
    def full_name(self) -> str:
        """The full name of this Collection.

        The full name is of the form database_name.collection_name."""
        return f"{self.database.name}.{self._name}"

    @property
    def database(self) -> "Database":
        """The database this collection belongs to"""
        return self._database

    @with_doc_and_sig(_Collection.aggregate)
    def aggregate(self, *args, **kwargs):
        return CommandCursor(self, "aggregate", *args, **kwargs)

    @with_doc_and_sig(_Collection.aggregate_raw_batches)
    def aggregate_raw_batches(self, *args, **kwargs):
        return RawBatchCommandCursor(
            self, "aggregate_raw_batches", *args, **kwargs
        )

    @with_doc_and_sig(_Collection.find)
    def find(self, *args, **kwargs):  # pylint: disable=missing-docstring
        return Cursor(self, *args, **kwargs)

    @with_doc_and_sig(_Collection.find_raw_batches)
    def find_raw_batches(
        self, *args, **kwargs
    ):  # pylint: disable=missing-docstring
        return RawBatchCursor(self, *args, **kwargs)

    @with_doc_and_sig(_Collection.rename)
    def rename(self, new_name: str, *args, **kwargs):
        return_value = self.request(
            pymongo_attr_name="distinct",
            pymongo_args=[new_name, *args],
            pymongo_kwargs=kwargs,
        )
        self._name = new_name
        return return_value

    @with_doc_and_sig(_Collection.watch)
    def watch(self, *args, **kwargs):  # pylint: disable=missing-docstring
        return CollectionChangeStream(self, *args, **kwargs)

    def build_payload(  # pylint: disable=dangerous-default-value
        self,
        *,
        pymongo_attr_name: Optional[str] = None,
        pymongo_args: Optional[List[Any]] = [],
        pymongo_kwargs: Optional[Dict[str, Any]] = {},
    ) -> Dict[str, Any]:
        payload = self.database.build_payload(
            pymongo_attr_name=pymongo_attr_name,
            pymongo_args=pymongo_args,
            pymongo_kwargs=pymongo_kwargs,
        )

        payload.update(
            col=self.name,
            col_ar=self.serialize_for_request(self._init_args),
            col_kw=self.serialize_for_request(self._init_kwargs),
        )

        return payload
