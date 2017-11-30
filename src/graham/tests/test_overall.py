import json

import attr
import marshmallow

import graham
import graham.fields


# Related topics:
#   https://github.com/python-attrs/attrs/issues/140

# example and basic test

@graham.schemify(
    tag='leaf',
    version='6e2f8588-73b2-4d45-a03e-9dbfb584c850',
)
@attr.s
class Leaf(object):
    name = attr.ib(
        default='<unnamed leaf>',
    )
    graham.attrib(
        attribute=name,
        field=marshmallow.fields.String(),
    )


@graham.schemify(
    tag='group',
    version='cb66bfae-ba3e-4b68-bbac-fb8cb5a30536',
)
@attr.s
class Group(object):
    name = attr.ib(
        default='<unnamed group>',
    )
    graham.attrib(
        attribute=name,
        field=marshmallow.fields.String(),
    )

    groups = attr.ib(
        default=attr.Factory(list),
    )
    graham.attrib(
        attribute=groups,
        field=marshmallow.fields.Nested('self', many=True),
    )

    leaves = attr.ib(
        default=attr.Factory(list),
    )
    graham.attrib(
        attribute=leaves,
        field=marshmallow.fields.List(
            marshmallow.fields.Nested(graham.schema(Leaf))
        ),
    )

    mixed_list = attr.ib(
        default=attr.Factory(list),
    )
    graham.attrib(
        attribute=mixed_list,
        field=graham.fields.MixedList(fields=(
            marshmallow.fields.Nested('Group'),
            marshmallow.fields.Nested(graham.schema(Leaf)),
        )),
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
