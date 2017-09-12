import functools
import json

import attr
import marshmallow


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


def create_schema(cls):
    class Schema(marshmallow.Schema):
        class Meta:
            include = {
                attribute.name: attribute.metadata[
                    metadata_key].field
                for attribute in attr.fields(cls)
            }
            ordered = True

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


def schemify(cls):
    cls.__graham_graham__ = Attributes(
        schema=create_schema(cls)())

    return cls


def register(cls):
    marshmallow.class_registry.register('Group', schema(cls))


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

def _strip_leading_underscore(s):
    return s if s[0] != '_' else s[1:]


def _dict_strip(d, keys):
    return {
        _strip_leading_underscore(k): v
        for k, v in d.items()
        # if k not in keys
    }


def set_type(name):
    def inner(cls):
        setattr(cls, type_attribute_name, type_attribute(name))

        return cls

    return inner


class fields:
    class MixedList(marshmallow.fields.Field):
        def __init__(self, *args, **kwargs):
            fields = kwargs.pop('fields')
            super().__init__(*args, **kwargs)

            self.instances = []

            for cls_or_instance in fields:
                if isinstance(cls_or_instance, type):
                    if not issubclass(cls_or_instance,
                                      marshmallow.fields.FieldABC):
                        raise ValueError('The type of the list elements '
                                         'must be a subclass of '
                                         'marshmallow.base.FieldABC')
                    self.instances.append(cls_or_instance())
                else:
                    if not isinstance(cls_or_instance,
                                      marshmallow.fields.FieldABC):
                        raise ValueError('The instances of the list '
                                         'elements must be of type '
                                         'marshmallow.base.FieldABC')
                    self.instances.append(cls_or_instance)

        def get_cls_or_instance(self, cls_or_instance):
            if not isinstance(self.instances, dict):
                instances = {}
                for instance in self.instances:
                    if isinstance(instance, marshmallow.fields.Nested):
                        nested = instance.nested
                        if isinstance(nested, str):
                            if nested == marshmallow.fields._RECURSIVE_NESTED:
                                instances[
                                    self.parent.type_tag] = self.parent
                            else:
                                cls = marshmallow.class_registry.get_class(
                                    nested)
                                instances[cls.type_tag] = cls
                        else:
                            instances[nested.type_tag] = nested
                    else:
                        instances[instance.type_tag] = instance

                self.instances = instances

            # TODO: handle self referential schema definition
            # self.cls_or_instance['group'] = Group.schema

            return self.instances[cls_or_instance]

        def _serialize(self, value, attr, obj):
            return [dump(each).data for each in value]

        def _deserialize(self, value, attr, data):
            return [
                self.get_cls_or_instance(each[type_attribute_name])
                    .load(_dict_strip(each, (type_attribute_name,))).data
                for each in value
            ]
