import textwrap

import attr
import marshmallow
import pytest

import graham


type_name = graham.core.type_attribute_name
version_name = graham.core.version_attribute_name


def rstrip_lines(s):
    return '\n'.join(line.rstrip() for line in s.splitlines())


def test_missing_metadata():
    with pytest.raises(graham.core.MissingMetadata, match='`test`'):
        @graham.schemify(tag='test')
        @attr.s
        class Test(object):
            test = attr.ib()

    @graham.schemify(tag='test')
    @attr.s
    class Test(object):
        test = attr.ib(default=None)


def test_dumps():
    @graham.schemify(tag='test')
    @attr.s
    class Test(object):
        test = attr.ib()
        graham.attrib(
            attribute=test,
            field=marshmallow.fields.String(),
        )

    test = Test(test='test')

    raw = graham.core.dumps(test).data
    assert raw == '{{"{}": "test", "test": "test"}}'.format(type_name)

    indented = graham.core.dumps(test, indent=4).data
    assert rstrip_lines(indented) == textwrap.dedent('''\
    {{
        "{}": "test",
        "test": "test"
    }}'''.format(type_name))


def test_strict():
    @graham.schemify(tag='test', strict=True)
    @attr.s
    class Test(object):
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
    class Test(object):
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
    class Test(object):
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


def test_load_wrong_tag():
    tag = 'test'

    @graham.schemify(tag=tag)
    @attr.s
    class Test(object):
        pass

    serialized = '{{"{tag_name}": "{tag}"}}'
    serialized = serialized.format(
        tag_name=type_name,
        tag=tag + '-',
    )

    with pytest.raises(
            marshmallow.exceptions.ValidationError,
            match=repr(type_name),
    ):
        graham.schema(Test).loads(serialized).data


def test_load_missing_tag():
    tag = 'test'

    @graham.schemify(tag=tag)
    @attr.s
    class Test(object):
        pass

    serialized = '{}'

    with pytest.raises(
            marshmallow.exceptions.ValidationError,
            match=repr(type_name),
    ):
        graham.schema(Test).loads(serialized).data


def test_load_wrong_version():
    tag = 'test'
    version = 42

    @graham.schemify(tag=tag, version=version)
    @attr.s
    class Test(object):
        pass

    serialized = '{{"{tag_name}": "{tag}", "{version_name}": {version}}}'
    serialized = serialized.format(
        tag_name=type_name,
        tag=tag,
        version_name=version_name,
        version=version + 1,
    )

    with pytest.raises(
            marshmallow.exceptions.ValidationError,
            match=repr(version_name),
    ):
        graham.schema(Test).loads(serialized).data


def test_load_missing_version():
    tag = 'test'
    version = 42

    @graham.schemify(tag=tag, version=version)
    @attr.s
    class Test(object):
        pass

    serialized = '{{"{tag_name}": "{tag}"}}'
    serialized = serialized.format(
        tag_name=type_name,
        tag=tag,
    )

    with pytest.raises(
            marshmallow.exceptions.ValidationError,
            match=repr(version_name),
    ):
        graham.schema(Test).loads(serialized).data


def test_dump_no_version():
    tag = 'test'

    @graham.schemify(tag=tag)
    @attr.s
    class Test(object):
        pass

    serialized = '{{"{tag_name}": "{tag}"}}'
    serialized = serialized.format(
        tag_name=type_name,
        tag=tag,
    )

    assert graham.dumps(Test()).data == serialized


def test_dump_version():
    tag = 'test'
    version = 42

    @graham.schemify(tag=tag, version=version)
    @attr.s
    class Test(object):
        pass

    serialized = '{{"{tag_name}": "{tag}", "{version_name}": {version}}}'
    serialized = serialized.format(
        tag_name=type_name,
        tag=tag,
        version_name=version_name,
        version=version,
    )

    assert graham.dumps(Test()).data == serialized


