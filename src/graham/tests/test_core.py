import textwrap

import attr
import marshmallow
import pytest

import graham


type_name = graham.core.type_attribute_name


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
        test = attr.ib()
        graham.attrib(
            attribute=test,
            field=marshmallow.fields.String(),
        )

    test = Test(test='test')

    raw = graham.core.dumps(test).data
    assert raw == '{{"{}": "test", "test": "test"}}'.format(type_name)

    indented = graham.core.dumps(test, indent=4).data
    assert indented == textwrap.dedent('''\
    {{
        "{}": "test",
        "test": "test"
    }}'''.format(type_name))


def test_strict():
    @graham.schemify(tag='test', strict=True)
    @attr.s
    class Test:
        email = attr.ib()
        graham.attrib(
            attribute=email,
            field=marshmallow.fields.Email(),
        )

    with pytest.raises(marshmallow.exceptions.ValidationError):
        graham.schema(Test).loads('{"email": "invalid"}')


def test_nonserialized():
    @graham.schemify(tag='test')
    @attr.s
    class Test:
        test = attr.ib()
        graham.attrib(
            attribute=test,
            field=marshmallow.fields.String(),
        )

        nope = attr.ib(default=None)

    test = Test(test='test')

    serialized = '{{"{}": "test", "test": "test"}}'.format(type_name)

    assert graham.dumps(test).data == serialized
    assert graham.schema(Test).loads(serialized).data == test


def test_load_from_dump_to():
    @graham.schemify(tag='test')
    @attr.s
    class Test:
        test = attr.ib()
        graham.attrib(
            attribute=test,
            field=marshmallow.fields.String(
                load_from='test_load_dump',
                dump_to='test_load_dump',
            )
        )

    test = Test(test='test string')

    serialized = '{{"{}": "test", "test_load_dump": "test string"}}'.format(
        type_name,
    )

    assert graham.dumps(test).data == serialized
    assert graham.schema(Test).loads(serialized).data == test
