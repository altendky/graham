import json

import attr
import marshmallow

import graham
import graham.fields


# Related topics:
#   https://github.com/python-attrs/attrs/issues/140

# example and basic test

@graham.schemify(tag='leaf')
@attr.s
class Leaf:
    name = attr.ib(
        default='<unnamed leaf>',
        metadata={
            **graham.create_metadata(field=marshmallow.fields.String()),
        }
    )


@graham.schemify(tag='group')
@attr.s
class Group:
    name = attr.ib(
        default='<unnamed group>',
        metadata=graham.create_metadata(
            field=marshmallow.fields.String()
        ),
    )
    groups = attr.ib(
        default=attr.Factory(list),
        metadata=graham.create_metadata(
            field=marshmallow.fields.Nested('self', many=True)
        ),
    )
    leaves = attr.ib(
        default=attr.Factory(list),
        metadata=graham.create_metadata(
            field=marshmallow.fields.List(
                marshmallow.fields.Nested(graham.schema(Leaf))
            ),
        ),
    )

    mixed_list = attr.ib(
        default=attr.Factory(list),
        metadata=graham.create_metadata(
            field=graham.fields.MixedList(fields=(
                marshmallow.fields.Nested('Group'),
                marshmallow.fields.Nested(graham.schema(Leaf)),
            )),
        ),
    )


def test_overall():
    # Attempt to recreate the List vs. many=True issues
    #   https://repl.it/KFXo/3

    subgroup = Group(name='subgroup')
    subgroup.leaves.append(Leaf(name='subgroup leaf'))

    group = Group()
    group.groups.append(subgroup)
    group.leaves.append(Leaf())
    group.mixed_list.append(Leaf(name='mixed list leaf'))
    group.mixed_list.append(Group(name='mixed list group'))

    def json_dumps(instance):
        return json.dumps(attr.asdict(instance), indent=4)

    print(' - - - - - - before')
    print(json_dumps(group))

    marshalled = graham.dumps(group)
    print()
    print(' - - - - - - serialized type', type(marshalled.data))
    unmarshalled = graham.schema(Group).loads(marshalled.data)
    print()
    print(' - - - - - - after')
    print(json_dumps(unmarshalled.data))

    print()
    print(' - - - - - - Original is equal to serialized/deserialized?')
    print(unmarshalled.data == group)
    assert unmarshalled.data == group
