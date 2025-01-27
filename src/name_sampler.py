import json
import random
from pathlib import Path

from src.time_period import TimePeriod

# Dictionary mapping surnames to their prefixes and weights
SURNAME_PREFIXES: dict[str, tuple[str, float]] = {
    "SANTOS": ("dos", 0.9),
    "SILVA": ("da", 0.9),
    "NASCIMENTO": ("do", 0.9),
    "COSTA": ("da", 0.9),
    "SOUZA": ("de", 0.8),
    "SOUSA": ("de", 0.8),
    "OLIVEIRA": ("de", 0.8),
    "JESUS": ("de", 0.8),
    "PEREIRA": ("da", 0.6),
    "FERREIRA": ("da", 0.6),
    "LIMA": ("de", 0.6),
    "CARVALHO": ("de", 0.6),
    "RIBEIRO": ("do", 0.6),
}


class BrazilianNameSampler:
    def __init__(self, json_file_path: str | Path | dict) -> None:
        """Initialize the name sampler with population data.
        Now accepts either a file path or pre-loaded data.

        Args:
            json_file_path: Path to JSON file or pre-loaded data dictionary

        """
        if isinstance(json_file_path, str | Path):
            with Path(json_file_path).open(encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = json_file_path

        if "common_names_percentage" not in data:
            msg = "Missing 'common_names_percentage' data"
            raise ValueError(msg)

        self.name_data = data["common_names_percentage"]
        if "surnames" not in data:
            msg = "Missing 'surnames' data"
            raise ValueError(msg)

        self.surname_data = data["surnames"]
        self.top_40_surnames = data["surnames"].get("top_40", {})
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate the name data structure has all required time periods and correct format.

        Raises:
            ValueError: If any required data structure is missing or invalid

        """
        for period in TimePeriod:
            if period.value not in self.name_data:
                msg = f"Missing data for time period: {period.value}"
                raise ValueError(msg)

            period_data = self.name_data[period.value]
            if not {"names", "total"}.issubset(period_data.keys()):
                msg = f"Invalid data structure for period {period.value}. Must contain 'names' and 'total'"
                raise ValueError(msg)

    def _apply_prefix(self, surname: str) -> str:
        """Apply prefix to surname based on predefined rules and probabilities.

        Args:
            surname: The surname to potentially prefix

        Returns:
            The surname with or without prefix based on probability

        """
        surname_upper = surname.upper()
        if surname_upper in SURNAME_PREFIXES:
            prefix, weight = SURNAME_PREFIXES[surname_upper]
            if random.random() < weight:
                return f"{prefix} {surname}"
        return surname

    def get_random_surname(self, top_40: bool = False, raw: bool = False, with_only_one_surname: bool = False) -> str:
        """Get random surname(s), optionally from top 40 only.

        Args:
            top_40: If True, only select from top 40 surnames
            raw: If True, returns surname in original format
            with_only_one_surname: If True, returns only one surname

        Returns:
            One or two surnames with appropriate prefixes

        """
        source = self.top_40_surnames if top_40 else self.surname_data
        surnames = []
        weights = []

        for surname, info in source.items():
            if surname != "top_40":  # Skip the top_40 nested dictionary
                surnames.append(surname)
                weights.append(info["percentage"])

        # Get first surname
        surname1 = random.choices(surnames, weights=weights, k=1)[0]
        surname1 = surname1 if raw else surname1.title()
        surname1 = self._apply_prefix(surname1)

        if with_only_one_surname:
            return surname1

        # Get second surname
        surname2 = random.choices(surnames, weights=weights, k=1)[0]
        surname2 = surname2 if raw else surname2.title()
        surname2 = self._apply_prefix(surname2)

        return f"{surname1} {surname2}"

    def get_random_name(
        self,
        time_period: TimePeriod = TimePeriod.UNTIL_2010,
        raw: bool = False,
        include_surname: bool = True,
        top_40: bool = False,
        with_only_one_surname: bool = False,
    ) -> str:
        """Get a random name from the specified time period.

        Args:
            time_period: Historical period to sample from
            raw: If True, returns name in original format, if False, converts to Title Case

        """
        period_data = self.name_data[time_period.value]
        names_data = period_data["names"]

        names = []
        weights = []
        for name, info in names_data.items():
            names.append(name)
            weights.append(info["percentage"])

        name = random.choices(names, weights=weights, k=1)[0]
        return name if raw else name.title()
from pathlib import Path

from src.time_period import TimePeriod


class BrazilianNameSampler:
    def __init__(self, json_file_path: str | Path | dict) -> None:
        """Initialize the name sampler with population data.
        Now accepts either a file path or pre-loaded data.

        Args:
            json_file_path: Path to JSON file or pre-loaded data dictionary

        """
        if isinstance(json_file_path, str | Path):
            with Path(json_file_path).open(encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = json_file_path

        if "common_names_percentage" not in data:
            msg = "Missing 'common_names_percentage' data"
            raise ValueError(msg)

        self.name_data = data["common_names_percentage"]
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate the name data structure has all required time periods and correct format.

        Raises:
            ValueError: If any required data structure is missing or invalid

        """
        for period in TimePeriod:
            if period.value not in self.name_data:
                msg = f"Missing data for time period: {period.value}"
                raise ValueError(msg)

            period_data = self.name_data[period.value]
            if not {"names", "total"}.issubset(period_data.keys()):
                msg = f"Invalid data structure for period {period.value}. Must contain 'names' and 'total'"
                raise ValueError(msg)

    def get_random_name(self, time_period: TimePeriod = TimePeriod.UNTIL_2010, raw: bool = False) -> str:
        """Get a random name from the specified time period.

        Args:
            time_period: Historical period to sample from
            raw: If True, returns name in original format, if False, converts to Title Case

        """
        period_data = self.name_data[time_period.value]
        names_data = period_data["names"]

        names = []
        weights = []
        for name, info in names_data.items():
            names.append(name)
            weights.append(info["percentage"])

        name = random.choices(names, weights=weights, k=1)[0]
        return name if raw else name.title()
