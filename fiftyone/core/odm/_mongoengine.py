class BaseDocument:
    def __init__(self, *args, **values):
        self._initialised = False
        self._created = True

        if args:
            raise TypeError(
                "Instantiating a document with positional arguments is not "
                "supported. Please use `field_name=value` keyword arguments."
            )

        __auto_convert = values.pop("__auto_convert", True)

        _created = values.pop("_created", True)

        signals.pre_init.send(self.__class__, document=self, values=values)

        # Check if there are undefined fields supplied to the constructor,
        # if so raise an Exception.
        if not self._dynamic and (self._meta.get("strict", True) or _created):
            _undefined_fields = set(values.keys()) - set(
                list(self._fields.keys()) + ["id", "pk", "_cls", "_text_score"]
            )
            if _undefined_fields:
                msg = f'The fields "{_undefined_fields}" do not exist on the document "{self._class_name}"'
                raise FieldDoesNotExist(msg)

        if self.STRICT and not self._dynamic:
            self._data = StrictDict.create(allowed_keys=self._fields_ordered)()
        else:
            self._data = {}

        self._dynamic_fields = SON()

        # Assign default values for fields
        # not set in the constructor
        for field_name in self._fields:
            if field_name in values:
                continue
            value = getattr(self, field_name, None)
            setattr(self, field_name, value)

        if "_cls" not in values:
            self._cls = self._class_name

        # Set actual values
        dynamic_data = {}
        FileField = _import_class("FileField")
        for key, value in values.items():
            field = self._fields.get(key)
            if field or key in ("id", "pk", "_cls"):
                if __auto_convert and value is not None:
                    if field and not isinstance(field, FileField):
                        value = field.to_python(value)
                setattr(self, key, value)
            else:
                if self._dynamic:
                    dynamic_data[key] = value
                else:
                    # For strict Document
                    self._data[key] = value

        # Set any get_<field>_display methods
        self.__set_field_display()

        if self._dynamic:
            self._dynamic_lock = False
            for key, value in dynamic_data.items():
                setattr(self, key, value)

        # Flag initialised
        self._initialised = True
        self._created = _created

        signals.post_init.send(self.__class__, document=self)

    def __delattr__(self, *args, **kwargs):
        ...

    def __setattr__(self, name, value):
        ...

    def __getstate__(self):
        ...

    def __setstate__(self, data):
        ...

    def __iter__(self):
        ...

    def __getitem__(self, name):
        ...

    def __setitem__(self, name, value):
        ...

    def __contains__(self, name):
        ...

    def __len__(self):
        ...

    def clean(self):
        ...

    def get_text_score(self):
        ...

    def to_mongo(self, use_db_field=True, fields=None):
        ...

    def validate(self, clean=True):
        ...

    def to_json(self, *args, **kwargs):
        ...

    @classmethod
    def from_json(cls, json_data, created=False, **kwargs):
        ...

    def __expand_dynamic_values(self, name, value):
        ...

    def _mark_as_changed(self, key):
        ...

    def _clear_changed_fields(self):
        ...

    @staticmethod
    def _nestable_types_clear_changed_fields(data):
        ...

    @staticmethod
    def _nestable_types_changed_fields(changed_fields, base_key, data):
        ...

    def _get_changed_fields(self):
        ...

    def _delta(self):
        ...

    @classmethod
    def _get_collection_name(cls):
        ...

    @classmethod
    def _from_son(cls, son, _auto_dereference=True, created=False):
        ...

    @classmethod
    def _build_index_specs(cls, meta_indexes):
        ...

    @classmethod
    def _build_index_spec(cls, spec):
        ...

    @classmethod
    def _unique_with_indexes(cls, namespace=""):
        ...

    @classmethod
    def _geo_indices(cls, inspected=None, parent_field=None):
        ...

    @classmethod
    def _lookup_field(cls, parts):
        ...

    @classmethod
    def _translate_field_name(cls, field, sep="."):
        ...

    def __set_field_display(self):
        ...

    def __get_field_display(self, field):
        ...


class EmbeddedDocument(BaseDocument):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instance = None
        self._changed_fields = []

    def __getstate__(self):
        data = super().__getstate__()
        data["_instance"] = None
        return data

    def __setstate__(self, state):
        super().__setstate__(state)
        self._instance = state["_instance"]

    def to_mongo(self, *args, **kwargs):
        data = super().to_mongo(*args, **kwargs)

        # remove _id from the SON if it's in it and it's None
        if "_id" in data and data["_id"] is None:
            del data["_id"]

        return data


class Document(BaseDocument):
    @property
    def pk(self):
        ...

    @pk.setter
    def pk(self, value):
        ...

    @classmethod
    def _get_db(cls):
        ...

    @classmethod
    def _disconnect(cls):
        ...

    @classmethod
    def _get_collection(cls):
        ...

    @classmethod
    def _get_capped_collection(cls):
        ...

    def to_mongo(self, *args, **kwargs):
        ...

    def modify(self, query=None, **update):
        ...

    def save(
        self,
        force_insert=False,
        validate=True,
        clean=True,
        write_concern=None,
        cascade=None,
        cascade_kwargs=None,
        _refs=None,
        save_condition=None,
        signal_kwargs=None,
        **kwargs,
    ):
        ...

    def _save_create(self, doc, force_insert, write_concern):
        ...

    def _get_update_doc(self):
        ...

    def _integrate_shard_key(self, doc, select_dict):
        ...

    def _save_update(self, doc, save_condition, write_concern):
        ...

    def cascade_save(self, **kwargs):
        ...

    @property
    def _qs(self):
        ...

    @property
    def _object_key(self):
        ...

    def update(self, **kwargs):
        ...

    def delete(self, signal_kwargs=None, **write_concern):
        ...

    def switch_db(self, db_alias, keep_created=True):
        ...

    def switch_collection(self, collection_name, keep_created=True):
        ...

    def select_related(self, max_depth=1):
        ...

    def reload(self, *fields, **kwargs):
        ...

    def _reload(self, key, value):
        ...

    def to_dbref(self):
        ...

    @classmethod
    def register_delete_rule(cls, document_cls, field_name, rule):
        ...

    @classmethod
    def drop_collection(cls):
        ...

    @classmethod
    def create_index(cls, keys, background=False, **kwargs):
        ...

    @classmethod
    def ensure_index(cls, key_or_list, background=False, **kwargs):
        ...

    @classmethod
    def ensure_indexes(cls):
        ...

    @classmethod
    def list_indexes(cls):
        ...

    @classmethod
    def compare_indexes(cls):
        ...


class DynamicDocument(Document):
    def __delattr__(self, *args, **kwargs):
        """Delete the attribute by setting to None and allowing _delta
        to unset it.
        """
        field_name = args[0]
        if field_name in self._dynamic_fields:
            setattr(self, field_name, None)
            self._dynamic_fields[field_name].null = False
        else:
            super().__delattr__(*args, **kwargs)
