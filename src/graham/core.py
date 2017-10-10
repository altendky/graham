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


metadata_key = object()
type_attribute_name = '_type'


@attr.s
class Metadata:
    field = attr.ib()


def create_metadata(*args, **kwargs):
    return {metadata_key: Metadata(*args, **kwargs)}


def create_schema(cls, **kwargs):
    include = {}
    for attribute in attr.fields(cls):
        try:
            metadata = attribute.metadata[metadata_key]
        except KeyError as e:
            raise MissingMetadata(
                'Metadata not found for {}.{}'.format(
                    cls.__name__,
                    attribute.name,
                ),
            ) from e

        include[attribute.name] = metadata.field

    class Schema(marshmallow.Schema):
        Meta = type(
            'Meta',
            (),
            {
                'include': include,
                **kwargs,
            }
        )

        # TODO: seems like this ought to be a static method
        @marshmallow.post_load
        def deserialize(self, data):
            # print(cls, data, attr.fields(cls))
            return cls(**_dict_strip(data, (type_attribute_name,)))

    Schema.__name__ = cls.__name__ + 'Schema'
    Schema.type_tag = getattr(attr.fields(cls), type_attribute_name).default

    return Schema


def dump(instance, *args, **kwargs):
    return schema(instance).dump(instance, *args, **kwargs)


def dumps(instance, *args, **kwargs):
    return schema(instance).dumps(instance, *args, **kwargs)


def schema(instance):
    return instance.__graham_graham__.schema


def schemify(**kwargs):
    kwargs.setdefault('ordered', True)
    kwargs.setdefault('strict', True)

    def inner(cls):
        cls.__graham_graham__ = Attributes(
            schema=create_schema(cls=cls, **kwargs)())

        return cls

    return inner


def register(cls):
    marshmallow.class_registry.register(cls.__name__, schema(cls))


def type_attribute(name):
    def validate(instance, attribute, value):
        # TODO: probably just really an unneeded double check since the
        # type is picked based on the type in the dict anyways...
        if value != attribute.default:
            raise UnmatchedTypeError(
                '{class_name}.{attribute_name} should be `{default}` '
                'but `{actual}` received'.format(
                    class_name=type(instance).__name__,
                    attribute_name=attribute.name,
                    default=attribute.default,
                    actual=value,
                )
            )

    return attr.ib(
        default=name,
        # init=False,
        validator=validate,
        metadata={
            **create_metadata(marshmallow.fields.String()),
        }
    )


# TODO: somehow confuses the schema completely
# def attrib(attribute, field):
#     attribute.metadata[metadata_key] = field
#     return attribute


def set_type(name):
    def inner(cls):
        setattr(cls, type_attribute_name, type_attribute(name))

        return cls

    return inner
