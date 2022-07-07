"""
| Copyright 2017-2022, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import abc
import functools
import inspect
import json
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    TypeVar,
)

import bson.json_util
import pymongo
import requests

TSource = TypeVar("TSource", bound=Callable)
TTarget = TypeVar("TTarget", bound=Callable)


def with_doc_and_sig(source_fn: TSource):  # pylint: disable=missing-docstring
    def _inner(target_fn: TTarget) -> TTarget:
        target_fn.__signature__ = inspect.signature(source_fn)
        target_fn.__doc__ = source_fn.__doc__
        return target_fn

    return _inner


def proxy(  # pylint: disable=missing-docstring
    source_fn: TSource, target_fn: TTarget
) -> TTarget:
    target_fn = with_doc_and_sig(source_fn)(target_fn)

    def _inner(*args, **kwargs) -> TTarget:
        inspect.signature(target_fn).bind(*args, **kwargs)
        return target_fn(*args, **kwargs)

    _inner.__name__ = source_fn.__name__
    return _inner


class MethodProxy(Protocol):  # pylint: disable=missing-docstring
    def __call__(
        self, method_name: str, instance: Any, *args: Any, **kwargs: Any
    ) -> float:
        ...


def _get_public_methods(obj):
    return (
        (name, member)
        for name, member in inspect.getmembers(obj)
        if not name.startswith("_") and inspect.isfunction(member)
    )


class PymongoProxyMeta(abc.ABCMeta):
    """Metaclass for proxying methods of an existing Pymongo class"""

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        return super().__prepare__(name, bases, **kwargs)

    def __new__(cls, name, bases, namespace, **kwargs):
        return super().__new__(cls, name, bases, namespace)

    def __init__(
        cls,
        name,
        bases,
        namespace,
        pymongo_cls,
        pymongo_method_proxy: MethodProxy,
    ):
        # Find implemented public methods on class
        already_implemented = dict(_get_public_methods(cls))

        # Find public methods on class to proxy
        for method_name, method in _get_public_methods(pymongo_cls):
            if method_name not in already_implemented:
                setattr(  # Set proxy method with method name
                    cls,
                    method_name,
                    proxy(
                        method,
                        functools.partial(pymongo_method_proxy, method_name),
                    ),
                )

        super().__init__(name, bases, namespace)


class PymongoAPIBase(abc.ABC):
    """Abstract base for making Pymongo requests to server"""

    @property
    @abc.abstractmethod
    def api_endpoint_url(self) -> str:
        """Endpoint of server"""
        ...

    def _build_payload(  # pylint: disable=dangerous-default-value
        self,
        pymongo_method_name: Optional[str] = None,
        pymongo_args: Optional[List[Any]] = [],
        pymongo_kwargs: Optional[Dict[str, Any]] = {},
    ) -> str:
        return dict(
            method_name=pymongo_method_name,
            args=bson.json_util.dumps(pymongo_args),
            kwargs=bson.json_util.dumps(pymongo_kwargs),
        )

    def build_payload(  # pylint: disable=dangerous-default-value
        self,
        pymongo_method_name: Optional[str] = None,
        pymongo_args: Optional[List[Any]] = [],
        pymongo_kwargs: Optional[Dict[str, Any]] = {},
    ) -> str:
        """Create serialized payload for request"""
        return json.dumps(
            self._build_payload(
                pymongo_method_name,
                pymongo_args,
                pymongo_kwargs,
            )
        )

    def _request(self, payload: str) -> Any:
        response = requests.post(url=self.api_endpoint_url, data=payload)
        try:
            response.raise_for_status()
        except requests.HTTPError as http_err:
            try:
                err_detail = response.json().get("detail")
                if "pymongo_err_cls" in err_detail:
                    error_cls = getattr(
                        pymongo.errors, err_detail["pymongo_err_cls"]
                    )
                    raise error_cls(
                        *err_detail["pymongo_err_args"]
                    ) from http_err
            except Exception:  # pylint: disable=broad-except
                ...  # Ignore any error when proxying Pymongo Error fails
            raise http_err

        return response.json()

    def request(  # pylint: disable=dangerous-default-value
        self,
        /,
        pymongo_method_name: Optional[str] = None,
        pymongo_args: Optional[List[Any]] = [],
        pymongo_kwargs: Optional[Dict[str, Any]] = {},
    ) -> Any:
        """Makes the request to the server"""
        payload = self.build_payload(
            pymongo_method_name, pymongo_args, pymongo_kwargs
        )
        return_value = self._request(payload)
        if return_value:
            return bson.json_util.loads(return_value)
        return return_value
