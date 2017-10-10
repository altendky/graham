import textwrap

import attr
import marshmallow
import pytest

import graham


def test_missing_metadata():
    with pytest.raises(graham.core.MissingMetadata, match='Test.test'):
        @graham.schemify
        @attr.s
        @graham.set_type('test')
        class Test:
            test = attr.ib()


def test_dumps():
    @graham.schemify
    @attr.s
    @graham.set_type('test')
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
