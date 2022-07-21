"""Unit tests for extract currents' load.py functions."""

from pathlib import Path

import pytest

from extract_currs.load import (
    get_path_from_config,
    get_parameters_path_from_config,
    get_final_parameters_path_from_config,
    get_protocols_path_from_config,
    get_features_path_from_config,
    get_morphology_from_recipe,
    get_morphology_from_config,
    get_recipe,
    get_apical_point_from_recipe_var_from_config,
)


test_config_dir = Path("tests/config")
morph_fname = "C230998A-I3_-_Scale_x1.000_y0.975_z1.000_-_Clone_2.asc"


def test_get_path_from_config():
    """Test get_path_from_config function."""
    config = {"path": "path0"}
    assert get_path_from_config(config, "path", "dir", "fname") == Path("path0")

    config = {"dir": "dir0", "fname": "fname0"}
    assert get_path_from_config(config, "path", "dir", "fname") == Path("dir0/fname0")

    config = {}
    with pytest.raises(KeyError, match="Could not find 'path' in configuration file."):
        get_path_from_config(config, "path", "dir", "fname")


def test_get_parameters_path_from_config():
    """Test get_parameters_path_from_config function."""
    config = {"params_path": "path0"}
    assert get_parameters_path_from_config(config) == Path("path0")

    config = {"params_dir": "dir0", "params_filename": "fname0"}
    assert get_parameters_path_from_config(config) == Path("dir0/fname0")

    config = {}
    with pytest.raises(
        KeyError, match="Could not find 'params_path' in configuration file."
    ):
        get_parameters_path_from_config(config)


def test_get_final_parameters_path_from_config():
    """Test get_final_parameters_path_from_config function."""
    config = {"final_params_path": "path0"}
    assert get_final_parameters_path_from_config(config) == Path("path0")

    config = {"final_params_dir": "dir0", "final_params_filename": "fname0"}
    assert get_final_parameters_path_from_config(config) == Path("dir0/fname0")

    config = {}
    with pytest.raises(
        KeyError, match="Could not find 'final_params_path' in configuration file."
    ):
        get_final_parameters_path_from_config(config)


def test_get_protocols_path_from_config():
    """Test get_protocols_path_from_config function."""
    config = {"protocols_path": "path0"}
    assert get_protocols_path_from_config(config) == Path("path0")

    config = {"protocols_dir": "dir0", "protocols_filename": "fname0"}
    assert get_protocols_path_from_config(config) == Path("dir0/fname0")

    config = {}
    with pytest.raises(
        KeyError, match="Could not find 'protocols_path' in configuration file."
    ):
        get_protocols_path_from_config(config)


def test_get_features_path_from_config():
    """Test get_features_path_from_config function."""
    config = {"features_path": "path0"}
    assert get_features_path_from_config(config) == Path("path0")

    config = {"features_dir": "dir0", "features_filename": "fname0"}
    assert get_features_path_from_config(config) == Path("dir0/fname0")

    config = {}
    with pytest.raises(
        KeyError, match="Could not find 'features_path' in configuration file."
    ):
        get_features_path_from_config(config)


def test_get_morphology_from_recipe():
    """Test get_morphology_from_recipe function."""
    morph_dir = str(test_config_dir / "morphology")
    recipe = {"morph_path": morph_dir, "morphology": [["_", morph_fname]]}

    morph = get_morphology_from_recipe(recipe)

    assert morph.morphology_path == str(Path(morph_dir) / morph_fname)


def test_get_morphology_from_config():
    """Test get_morphology_from_config function."""
    morph_dir = str(test_config_dir / "morphology")

    # case apical point isec is None
    config = {
        "morph_name": "_",
        "morph_dir": morph_dir,
        "morph_filename": morph_fname,
        "apical_point_isec": None,
    }
    morph, altmorph = get_morphology_from_config(config)

    assert morph.morphology_path == str(Path(morph_dir) / morph_fname)
    assert len(altmorph) == 1
    assert len(altmorph[0]) == 2
    assert altmorph[0][0] == "_"
    assert altmorph[0][1] == morph_fname

    # case apical point isec is not None
    config = {
        "morph_name": "_",
        "morph_dir": morph_dir,
        "morph_filename": morph_fname,
        "apical_point_isec": 14,
    }
    morph, altmorph = get_morphology_from_config(config)

    assert morph.morphology_path == str(Path(morph_dir) / morph_fname)
    assert len(altmorph) == 1
    assert len(altmorph[0]) == 3
    assert altmorph[0][0] == "_"
    assert altmorph[0][1] == morph_fname
    assert altmorph[0][2] == 14


def check_recipe(recipe):
    """Assert that recipe conforms to what is expected."""
    assert (
        recipe["morph_path"]
        == "/gpfs/bbp.cscs.ch/project/proj38/cells/hybrid-output-2016-12-23/04_ZeroDiameterFix-ASC/"
    )
    morph = recipe["morphology"]
    assert len(morph) == 1
    assert len(morph[0]) == 2
    assert morph[0][0] == "_"
    assert morph[0][1] == "C230998A-I3.asc"
    assert recipe["params"] == "config/params/int_noise.json"
    assert recipe["protocol"] == "config/protocols/bIR.json"
    assert recipe["features"] == "config/features/bIR.json"


def test_get_recipe():
    """Test get_recipe function."""
    # test data
    recipe_dir = test_config_dir / "recipes"
    recipe_fname = "recipes.json"
    recipe_path = recipe_dir / recipe_fname
    emodel = "bIR_L23BP"

    # case no recipe file indication in config
    with pytest.raises(
        KeyError, match="Could not find 'recipe_path' in configuration file."
    ):
        get_recipe({}, "emodel_name")

    # case recipe_path in config
    config = {"recipe_path": str(recipe_path)}
    recipe = get_recipe(config, emodel)
    check_recipe(recipe)

    # legacy case
    config = {"recipe_dir": str(recipe_dir), "recipe_filename": str(recipe_fname)}
    recipe = get_recipe(config, emodel)
    check_recipe(recipe)


def test_get_apical_point_from_recipe_var_from_config():
    """Test get_apical_point_from_recipe_var_from_config function."""
    with pytest.raises(
        KeyError,
        match="Could not find 'apical_point_from_recipe' in configuration file.",
    ):
        get_apical_point_from_recipe_var_from_config({})

    assert get_apical_point_from_recipe_var_from_config(
        {"apical_point_from_recipe": True}
    )
    assert not get_apical_point_from_recipe_var_from_config(
        {"apical_point_from_recipe": False}
    )
    assert get_apical_point_from_recipe_var_from_config({"etypetest": "random_string"})
    assert not get_apical_point_from_recipe_var_from_config({"etypetest": ""})
