"""
| Copyright 2017-2022, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import os
from typing import TYPE_CHECKING, Any, List, Dict, Optional, Union

from pymongo.change_stream import ChangeStream as _ChangeStream

from fiftyone.pymongo.util import PymongoWSBase, PymongoProxyMeta


if TYPE_CHECKING:
    from fiftyone.pymongo.client import Client
    from fiftyone.pymongo.database import Database
    from fiftyone.pymongo.collection import Collection


def _proxy(
    method_name: str,
    instance: "ChangeStream",
    *args,
    **kwargs,
) -> Any:
    return instance.request(
        pymongo_attr_name=method_name,
        pymongo_args=args,
        pymongo_kwargs=kwargs,
    )


class ChangeStream(
    PymongoWSBase,
    metaclass=PymongoProxyMeta,
    pymongo_cls=_ChangeStream,
    pymongo_method_proxy=_proxy,
):
    def __init__(
        self,
        target: Union["Client", "Database", "Collection"],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._target = target
        self.request()

    @property
    def api_endpoint_url(self) -> str:
        return os.path.join(
            self._target.api_endpoint_url.replace("http", "ws"),
            "change_stream",
        )

    def build_payload(
        self,
        *,
        pymongo_attr_name: Optional[str] = None,
        pymongo_args: Optional[List[Any]] = [],
        pymongo_kwargs: Optional[Dict[str, Any]] = {},
    ) -> str:
        payload = self._target.build_payload(
            pymongo_attr_name=pymongo_attr_name,
            pymongo_args=pymongo_args,
            pymongo_kwargs=pymongo_kwargs,
        )

        payload.update(
            cs_ar=self.serialize_for_request(self._init_args),
            cs_kw=self.serialize_for_request(self._init_kwargs),
        )
        return payload


class ClusterChangeStream(
    ChangeStream,
    pymongo_cls=_ChangeStream,
    pymongo_method_proxy=_proxy,
):
    def __init__(self, target: "Client", *args, **kwargs):
        super().__init__(target, *args, **kwargs)


class CollectionChangeStream(
    ChangeStream,
    pymongo_cls=_ChangeStream,
    pymongo_method_proxy=_proxy,
):
    def __init__(self, target: "Collection", *args, **kwargs):
        super().__init__(target, *args, **kwargs)


class DatabaseChangeStream(
    ChangeStream,
    pymongo_cls=_ChangeStream,
    pymongo_method_proxy=_proxy,
):
    def __init__(self, target: "Database", *args, **kwargs):
        super().__init__(target, *args, **kwargs)
