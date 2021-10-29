"""scrapli_cfg.diff"""
import difflib
import shutil
from typing import List, Tuple

from scrapli_cfg.exceptions import DiffConfigError
from scrapli_cfg.response import ScrapliCfgResponse

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
END_COLOR = "\033[0m"


class ScrapliCfgDiffResponse(ScrapliCfgResponse):
    def __init__(
        self, host: str, source: str, colorize: bool = True, side_by_side_diff_width: int = 0
    ) -> None:
        """
        Scrapli config diff object

        Args:
            host: host the diff is for
            source: source config store from the device, typically running|startup
            colorize: True/False colorize diff output
            side_by_side_diff_width: width to use to generate the side-by-side diff, if not provided
                will fetch the current terminal width

        Returns:
            N/A

        Raises:
            N/A

        """
        super().__init__(host=host, raise_for_status_exception=DiffConfigError)

        self.colorize = colorize
        self.side_by_side_diff_width = side_by_side_diff_width

        self.source = source
        self.source_config = ""
        self.candidate_config = ""
        self.device_diff = ""

        self._difflines: List[str] = []
        self.additions = ""
        self.subtractions = ""

        self._unified_diff = ""
        self._side_by_side_diff = ""

    def __repr__(self) -> str:
        """
        Magic repr method for ScrapliCfgResponse class

        Args:
            N/A

        Returns:
            str: repr for class object

        Raises:
            N/A

        """
        return f"ScrapliCfgDiffResponse <Success: {str(not self.failed)}>"

    def __str__(self) -> str:
        """
        Magic str method for ScrapliCfgDiffResponse class

        Args:
            N/A

        Returns:
            str: str for class object

        Raises:
            N/A

        """
        return f"ScrapliCfgDiffResponse <Success: {str(not self.failed)}>"

    def record_diff_response(
        self, source_config: str, candidate_config: str, device_diff: str
    ) -> None:
        """
        Scrapli config diff object

        Args:
            source_config: the actual contents of the source config
            candidate_config: the scrapli_cfg candidate config
            device_diff: diff generated by the device itself (if applicable)

        Returns:
            N/A

        Raises:
            N/A

        """
        self.source_config = source_config
        self.candidate_config = candidate_config
        self.device_diff = device_diff

        _differ = difflib.Differ()
        self._difflines = list(
            _differ.compare(
                self.source_config.splitlines(keepends=True),
                self.candidate_config.splitlines(keepends=True),
            )
        )

        self.additions = "".join([line[2:] for line in self._difflines if line[:2] == "+ "])
        self.subtractions = "".join([line[2:] for line in self._difflines if line[:2] == "- "])

    def _generate_colors(self) -> Tuple[str, str, str, str]:
        """
        Generate the necessary strings for colorizing or not output

        Args:
            N/A

        Returns:
            tuple: tuple of strings for colorizing (or not) output

        Raises:
            N/A

        """
        yellow = YELLOW if self.colorize else "? "
        red = RED if self.colorize else "- "
        green = GREEN if self.colorize else "+ "
        end = END_COLOR if self.colorize else ""
        return yellow, red, green, end

    @property
    def side_by_side_diff(self) -> str:
        """
        Generate a side-by-side diff of source vs candidate

        Args:
            N/A

        Returns:
            str: unified diff text

        Raises:
            N/A

        """
        if self._side_by_side_diff:
            return self._side_by_side_diff

        yellow, red, green, end = self._generate_colors()

        term_width = self.side_by_side_diff_width or shutil.get_terminal_size().columns
        half_term_width = int(term_width / 2)
        diff_side_width = int(half_term_width - 5)

        side_by_side_diff_lines = []
        for line in self._difflines:
            if line[:2] == "? ":
                current = (
                    yellow + f"{line[2:][:diff_side_width].rstrip() : <{half_term_width}}" + end
                )
                candidate = yellow + f"{line[2:][:diff_side_width].rstrip()}" + end
            elif line[:2] == "- ":
                current = red + f"{line[2:][:diff_side_width].rstrip() : <{half_term_width}}" + end
                candidate = ""
            elif line[:2] == "+ ":
                current = f"{'' : <{half_term_width}}"
                candidate = green + f"{line[2:][:diff_side_width].rstrip()}" + end
            else:
                current = f"{line[2:][:diff_side_width].rstrip() : <{half_term_width}}"
                candidate = f"{line[2:][:diff_side_width].rstrip()}"

            side_by_side_diff_lines.append(current + candidate)

        joined_side_by_side_diff = "\n".join(side_by_side_diff_lines)

        self._side_by_side_diff = joined_side_by_side_diff

        return self._side_by_side_diff

    @property
    def unified_diff(self) -> str:
        """
        Generate a unified diff of source vs candidate

        Args:
            N/A

        Returns:
            str: unified diff text

        Raises:
            N/A

        """
        if self._unified_diff:
            return self._unified_diff

        yellow, red, green, end = self._generate_colors()

        unified_diff = [
            yellow + line[2:] + end
            if line[:2] == "? "
            else red + line[2:] + end
            if line[:2] == "- "
            else green + line[2:] + end
            if line[:2] == "+ "
            else line[2:]
            for line in self._difflines
        ]
        joined_unified_diff = "".join(unified_diff)

        self._unified_diff = joined_unified_diff

        return self._unified_diff
