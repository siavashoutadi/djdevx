"""Unit tests for BaseDeployPlugin and DeployParam."""

from djdevx.deployment._base import BaseDeployPlugin, DeployParam


class TestDeployParam:
    """Tests for the DeployParam dataclass."""

    def test_deploy_param_defaults(self) -> None:
        param = DeployParam(name="test_param")
        assert param.name == "test_param"
        assert param.type_ is str
        assert param.help == ""
        assert param.default is None
        assert param.prompt is None
        assert param.hide_input is False

    def test_deploy_param_with_values(self) -> None:
        param = DeployParam(
            name="domain",
            type_=str,
            help="Domain name",
            default="example.com",
            prompt="Enter domain:",
            hide_input=True,
        )
        assert param.name == "domain"
        assert param.type_ is str
        assert param.help == "Domain name"
        assert param.default == "example.com"
        assert param.prompt == "Enter domain:"
        assert param.hide_input is True


class TestBaseDeployPlugin:
    """Tests for the BaseDeployPlugin class."""

    def test_has_default_name(self) -> None:
        plugin = BaseDeployPlugin()
        assert plugin.name == ""

    def test_has_default_generate_params(self) -> None:
        plugin = BaseDeployPlugin()
        assert plugin.generate_params == []

    def test_generate_raises_not_implemented(self) -> None:
        plugin = BaseDeployPlugin()
        try:
            plugin.generate(output_dir="/tmp/test")
            assert False, "Expected NotImplementedError"
        except NotImplementedError:
            pass

    def test_verify_raises_not_implemented(self) -> None:
        plugin = BaseDeployPlugin()
        try:
            plugin.verify(output_dir="/tmp/test")
            assert False, "Expected NotImplementedError"
        except NotImplementedError:
            pass
