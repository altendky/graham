import attr
import pytest

import graham


def test_missing_metadata():
    with pytest.raises(graham.core.MissingMetadata, match='Test.test'):
        @graham.schemify
        @attr.s
        @graham.set_type('test')
        class Test:
            test = attr.ib()
