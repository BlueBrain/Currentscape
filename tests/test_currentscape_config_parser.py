"""Test currentscape config parser."""

from logging import WARNING

from pytest import LogCaptureFixture

from currentscape.config_parser import check_config, replace_defaults


def test_check_config(caplog: LogCaptureFixture):
    """Test that check_config warns when discrepancy between patterns and line styles."""
    config = {
        "pattern": {"use": True, "patterns": ["", "/", "\\"]},
        "show": {"all_currents": True},
        "line": {"styles": ["solid", (0, (1, 1))]},
    }

    caplog.set_level(WARNING)
    check_config(config)
    assert (
        "currentscape.config_parser",
        WARNING,
        "line:styles should have as many items as pattern:patterns.",
    ) in caplog.record_tuples


def test_replace_defaults():
    """Test replace_defaults function."""
    # replace non-dict
    default_config = {"test": 1}
    user_config = {"test": 2}
    new_config = replace_defaults(default_config, user_config)
    assert new_config == {"test": 2}

    # add non-dict
    default_config = {}
    user_config = {"test": 2}
    new_config = replace_defaults(default_config, user_config)
    assert new_config == {"test": 2}

    # no input
    default_config = {"test": 1}
    user_config = {}
    new_config = replace_defaults(default_config, user_config)
    assert new_config == {"test": 1}

    # replace in dict
    default_config = {"test": {"inner": 1}}
    user_config = {"test": {"inner": 2}}
    new_config = replace_defaults(default_config, user_config)
    assert new_config == {"test": {"inner": 2}}

    # add item to dict
    default_config = {"test": {"inner": 1}}
    user_config = {"test": {"new": 2}}
    new_config = replace_defaults(default_config, user_config)
    assert new_config == {"test": {"inner": 1, "new": 2}}
