"""scrapli_cfg.platform.sync_platform"""
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Pattern, Tuple

from scrapli.driver import NetworkDriver
from scrapli_cfg.diff import ScrapliCfgDiffResponse
from scrapli_cfg.platform.base.base_platform import ScrapliCfgBase
from scrapli_cfg.response import ScrapliCfgResponse


class ScrapliCfg(ABC, ScrapliCfgBase):
    def __init__(
        self, conn: NetworkDriver, config_sources: List[str], on_open: Callable[..., Any]
    ) -> None:
        """
        Scrapli Config base class

        Args:
            conn: scrapli connection to use
            config_sources: list of config sources
            on_open: async callable to run at connection open

        Returns:
            None

        Raises:
            N/A

        """
        self.conn = conn
        self.on_open = on_open

        super().__init__(config_sources=config_sources)

    def open(self) -> None:
        """
        Open the connection and prepare for config operations

        Does "normal" scrapli open things, but also runs the _on_open method of scrapli config which
        generally does things like disable console logging

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self.logger.info("opening scrapli connection")

        if not self.conn.isalive():
            self.conn.open()

        self.logger.debug("executing scrapli_cfg on open method")
        self.on_open(self)

    @abstractmethod
    def get_config(self, source: str = "running") -> ScrapliCfgResponse:
        """
        Get device configuration

        Args:
            source: name of the config source, generally running|startup

        Returns:
            ScrapliCfgResponse: response object containing string of the target config source as the
                `result` attribute

        Raises:
            N/A

        """

    @abstractmethod
    def load_config(self, config: str, replace: bool = False, **kwargs: Any) -> ScrapliCfgResponse:
        """
        Load configuration to a device

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """

    @abstractmethod
    def abort_config(self) -> ScrapliCfgResponse:
        """
        Abort a configuration -- discards any loaded config

        Args:
            N/A

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """

    @abstractmethod
    def commit_config(self, source: str = "running") -> ScrapliCfgResponse:
        """
        Commit a loaded configuration

        Args:
            source: name of the config source to commit against, generally running|startup

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """

    @abstractmethod
    def diff_config(self, source: str = "running") -> ScrapliCfgDiffResponse:
        """
        Diff a loaded configuration against the source config store

        Args:
            source: name of the config source to diff against, generally running|startup -- device
                diffs will generally not care about this argument, but the built in scrapli differ
                will

        Returns:
            ScrapliCfgDiffResponse: scrapli cfg diff object

        Raises:
            N/A

        """

    def render_substituted_config(
        self,
        config_template: str,
        substitutes: List[Tuple[str, Pattern[str]]],
        source: str = "running",
    ) -> str:
        """
        Render a substituted configuration file

        Renders a configuration based on a user template, substitutes, and a target config from the
        device.

        Args:
            config_template: config file to use as the base for substitutions -- should contain
                jinja2-like variables that will be replaced with data fetched from the source config
                by the substitutes patterns
            substitutes: tuple of name, pattern -- where name matches the jinja2-like variable in
                the config_template file, and pattern is a compiled regular expression pattern to be
                used to fetch that section from the source config
            source: config source to use for the substitution efforts, typically running|startup

        Returns:
            str: substituted/rendered config

        Raises:
            N/A

        """
        self.logger.info("fetching configuration and replacing with provided substitutes")

        source_config = self.get_config(source=source)
        return self._render_substituted_config(
            config_template=config_template,
            substitutes=substitutes,
            source_config=source_config.result,
        )
