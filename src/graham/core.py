import collections

import attr
import marshmallow

from graham.utils import _dict_strip


class MissingMetadata(Exception):
    pass


class UnmatchedTypeError(Exception):
    pass


@attr.s
class Attributes(object):
    schema = attr.ib()
    type = attr.ib()
    version = attr.ib()


metadata_key = object()
type_attribute_name = '_type'
version_attribute_name = '_version'


@attr.s
class Metadata(object):
    field = attr.ib()


def attrib(attribute, *args, **kwargs):
    # https://github.com/python-attrs/attrs/issues/278
    if len(attribute.metadata) == 0:
        attribute.metadata = {}

    attribute.metadata.update(create_metadata(*args, **kwargs))

    return attribute


def create_metadata(*args, **kwargs):
    return {metadata_key: Metadata(*args, **kwargs)}


def validator(expected):
    def validate(actual, expected=expected):
        return actual == expected

    return validate


def create_schema(cls, tag, options, version):
    include = collections.OrderedDict()
    include[type_attribute_name] = marshmallow.fields.String(
        default=tag,
        required=True,
        validate=validator(tag),
    )
    if version is not None:
        include[version_attribute_name] = marshmallow.fields.String(
            default=version,
            required=True,
            validate=validator(version),
        )

    for attribute in attr.fields(cls):
        metadata = attribute.metadata.get(metadata_key)
        if metadata is None:
            if attribute.default is not attr.NOTHING:
                continue
            else:
                raise MissingMetadata(
                    'Metadata required for defaultless attribute `{}`'.format(
                        attribute.name,
                    ),
                )

        include[attribute.name] = metadata.field

    meta_dict = {
        'include': include,
    }
    meta_dict.update(options)

    class Schema(marshmallow.Schema):
        Meta = type(
            'Meta',
            (),
            meta_dict,
        )

        data_class = cls

        # TODO: seems like this ought to be a static method
        @marshmallow.post_load
        def deserialize(self, data):
            del data[type_attribute_name]
            if cls.__graham_graham__.version is not None:
                del data[version_attribute_name]

            return cls(**data)

    Schema.__name__ = cls.__name__ + 'Schema'
    setattr(
        Schema,
        type_attribute_name,
        marshmallow.fields.Constant(constant=tag),
    )
    setattr(
        Schema,
        version_attribute_name,
        marshmallow.fields.Constant(constant=version),
    )

    return Schema


def dump(instance, *args, **kwargs):
    return schema(instance).dump(instance, *args, **kwargs)


def dumps(instance, *args, **kwargs):
    return schema(instance).dumps(instance, *args, **kwargs)


def schema(instance):
    return instance.__graham_graham__.schema


def schemify(tag, version=None, **marshmallow_options):
    marshmallow_options.setdefault('ordered', True)
    marshmallow_options.setdefault('strict', True)

    def inner(cls):
        cls.__graham_graham__ = Attributes(
            schema=create_schema(
                cls=cls,
                tag=tag,
                version=version,
                options=marshmallow_options,
            )(),
            type=tag,
            version=version,
        )

        marshmallow.class_registry.register(cls.__name__, schema(cls))

        return cls

    return inner
