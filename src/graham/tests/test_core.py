import textwrap

import attr
import marshmallow
import pytest

import graham


def test_missing_metadata():
    with pytest.raises(graham.core.MissingMetadata, match='`test`'):
        @graham.schemify(tag='test')
        @attr.s
        class Test:
            test = attr.ib()

    @graham.schemify(tag='test')
    @attr.s
    class Test:
        test = attr.ib(default=None)


def test_dumps():
    @graham.schemify(tag='test')
    @attr.s
    class Test:
        test = attr.ib(
            metadata=graham.create_metadata(
                field=marshmallow.fields.String()
            ),
        )

    test = Test(test='test')

    raw = graham.core.dumps(test).data
    assert raw == '{"test": "test", "_type": "test"}'

    indented = graham.core.dumps(test, indent=4).data
    assert indented == textwrap.dedent('''\
    {
        "test": "test",
        "_type": "test"
    }''')


def test_strict():
    @graham.schemify(tag='test', strict=True)
    @attr.s
    class Test:
        email = attr.ib(
            metadata=graham.create_metadata(
                field=marshmallow.fields.Email()
            ),
        )

    with pytest.raises(marshmallow.exceptions.ValidationError):
        graham.schema(Test).loads('{"email": "invalid"}')


def test_nonserialized():
    @graham.schemify(tag='test')
    @attr.s
    class Test:
        test = attr.ib(
            metadata=graham.create_metadata(
                field=marshmallow.fields.String()
            ),
        )
        nope = attr.ib(default=None)

    test = Test(test='test')

    serialized = '{"test": "test", "_type": "test"}'

    assert graham.dumps(test).data == serialized
    assert graham.schema(Test).loads(serialized).data == test
