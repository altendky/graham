import json

import attr
import marshmallow.fields

import graham
import graham.fields


def test_mixed_list_exclude():
    @graham.schemify(tag='a')
    @attr.s
    class A(object):
        a = attr.ib(
            metadata=graham.create_metadata(
                field=marshmallow.fields.Integer(),
            )
        )

    @attr.s
    class B(object):
        b = attr.ib()

    @graham.schemify(tag='c')
    @attr.s
    class C(object):
        x = attr.ib(
            metadata=graham.create_metadata(
                field=graham.fields.MixedList(
                    fields=(
                        marshmallow.fields.Nested(graham.schema(A)),
                    ),
                    exclude=(
                        B,
                    ),
                )
            )
        )

    c = C(
        x=[
            A(a=1),
            A(a=2),
            B(b=3),
        ],
    )

    marshalled = graham.dumps(c)
    data = json.loads(marshalled.data)

    assert all(d['_type'] == 'a' for d in data['x'])
