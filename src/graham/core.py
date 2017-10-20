import collections

import attr
import marshmallow

from graham.utils import _dict_strip


class MissingMetadata(Exception):
    pass


class UnmatchedTypeError(Exception):
    pass


@attr.s
class Attributes:
    schema = attr.ib()
    type = attr.ib()


metadata_key = object()
type_attribute_name = '_type'


@attr.s
class Metadata:
    field = attr.ib()


def create_metadata(*args, **kwargs):
    return {metadata_key: Metadata(*args, **kwargs)}


def create_schema(cls, tag, options):
    include = collections.OrderedDict()
    include['_type'] = marshmallow.fields.Constant(constant=tag)

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

    class Schema(marshmallow.Schema):
        Meta = type(
            'Meta',
            (),
            {
                'include': include,
                **options,
            }
        )

        data_class = cls

        # TODO: seems like this ought to be a static method
        @marshmallow.post_load
        def deserialize(self, data):
            type_ = data.pop(type_attribute_name)
            if type_ != cls.__graham_graham__.type:
                raise UnmatchedTypeError(
                    '{class_name}.{attribute_name} should be `{default}` '
                    'but `{actual}` received'.format(
                        class_name=type(self).__name__,
                        attribute_name=type_attribute_name,
                        default=cls.__graham_graham__.type,
                        actual=type_,
                    )
                )

            return cls(**data)

    Schema.__name__ = cls.__name__ + 'Schema'
    Schema._type = marshmallow.fields.Constant(constant=tag)

    return Schema


def dump(instance, *args, **kwargs):
    return schema(instance).dump(instance, *args, **kwargs)


def dumps(instance, *args, **kwargs):
    return schema(instance).dumps(instance, *args, **kwargs)


def schema(instance):
    return instance.__graham_graham__.schema


def schemify(tag, **marshmallow_options):
    marshmallow_options.setdefault('ordered', True)
    marshmallow_options.setdefault('strict', True)

    def inner(cls):
        cls.__graham_graham__ = Attributes(
            schema=create_schema(
                cls=cls,
                tag=tag,
                options=marshmallow_options,
            )(),
            type=tag,
        )

        marshmallow.class_registry.register(cls.__name__, schema(cls))

        return cls

    return inner


# TODO: somehow confuses the schema completely
# def attrib(attribute, field):
#     attribute.metadata[metadata_key] = field
#     return attribute
