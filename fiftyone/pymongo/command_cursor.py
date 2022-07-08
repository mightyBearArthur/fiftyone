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
    Union,
)

from pymongo.command_cursor import CommandCursor as _CommandCursor

from fiftyone.pymongo.util import PymongoWSBase, PymongoProxyMeta

if TYPE_CHECKING:
    from fiftyone.pymongo.client import Client
    from fiftyone.pymongo.database import Database
    from fiftyone.pymongo.collection import Collection


def _proxy_return_self(
    method_name: str,
    instance: "CommandCursor",
    *args,
    **kwargs,
) -> Any:
    instance.request(
        pymongo_attr_name=method_name,
        pymongo_args=args,
        pymongo_kwargs=kwargs,
    )
    return instance


class CommandCursor(
    PymongoWSBase,
    metaclass=PymongoProxyMeta,
    pymongo_cls=_CommandCursor,
    pymongo_method_proxy=_proxy_return_self,
):
    """Proxy class for pymongo.cursor.Cursor"""

    def __init__(
        self,
        target: Union["Client", "Database", "Collection"],
        command: str,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._target = target
        self._command = command
        self.request()

    @property
    def api_endpoint_url(self) -> str:
        return os.path.join(
            self._target.api_endpoint_url.replace("http", "ws"),
            "command_cursor",
        )

    @property
    def address(self) -> Optional[Tuple[str, Any]]:
        return None

    @property
    def session(self) -> None:
        return None

    def build_payload(  # pylint: disable=dangerous-default-value
        self,
        *,
        pymongo_attr_name: Optional[str] = None,
        pymongo_args: Optional[List[Any]] = [],
        pymongo_kwargs: Optional[Dict[str, Any]] = {},
    ) -> Dict[str, Any]:
        payload = self._target.build_payload(
            pymongo_attr_name=pymongo_attr_name,
            pymongo_args=pymongo_args,
            pymongo_kwargs=pymongo_kwargs,
        )

        payload.update(
            crs_cmd=self._command,
            crs_ar=self.serialize_for_request(self._init_args),
            crs_kw=self.serialize_for_request(self._init_kwargs),
        )

        return payload


class RawBatchCommandCursor(
    CommandCursor,
    pymongo_cls=_CommandCursor,
    pymongo_method_proxy=_proxy_return_self,
):
    ...
