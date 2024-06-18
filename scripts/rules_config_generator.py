"""Generates the rules configuration from the rules files."""

from dataclasses import asdict, dataclass
import inspect
import json
from pathlib import Path
from typing import Any

from scripts.constants import RULES_FOLDER
from scripts.utils import read_content


@dataclass()
class RuleConfig:
    """Single rule configuration."""

    severity: str | None = None

    @classmethod
    def from_dict(cls, values: dict[str, Any]):
        """Creates a RuleConfig instance from a dictionary, ignoring extra keys."""

        return cls(
            **{
                k: v
                for k, v in values.items()
                if k in inspect.signature(cls).parameters
            }
        )


@dataclass
class RuleConfigWithDisabled(RuleConfig):
    """Single rule configuration with disabled flag."""

    disabled: bool | None = None


@dataclass
class CategoryRuleConfig:
    """Rules configuration for a single category."""

    rules_disabled: list[str]
    rules: dict[str, RuleConfig]
    minimum_severity: str | None = None


@dataclass
class RulesConfig:
    """All rules configurations."""

    iac: CategoryRuleConfig


class RulesConfigGenerator:
    """Generates all rules-related configurations."""

    def __init__(self, rules_config_path: Path):
        self.rules_config_path = rules_config_path

    def _get_rules_files(self) -> dict[str, RuleConfigWithDisabled]:
        """Returns all specific rules configs by ID."""

        files = self.rules_config_path.rglob("*-AVD-*.yml")
        return {
            file.stem: RuleConfigWithDisabled(**read_content(file)) for file in files
        }

    def _partition_rules_disabled(
        self, rules: dict[str, RuleConfigWithDisabled]
    ) -> tuple[dict[str, RuleConfig], list[str]]:
        """
        Partitions the rules into a list of disabled rules,
        and a dict of enabled rules and their config.
        Removes the "disabled" key from the enabled rules config.
        """

        disabled_rules: list[str] = []
        enabled_rules: dict[str, RuleConfig] = {}

        for rule_id, rule_config in rules.items():
            if rule_config.disabled:
                disabled_rules.append(rule_id)
            else:
                enabled_rules[rule_id] = RuleConfig.from_dict(rule_config.__dict__)

        return enabled_rules, disabled_rules

    def generate(self) -> RulesConfig:
        """Reads, processes and returns the rules configuration from each rule file ."""

        defaults = read_content(self.rules_config_path / "iac" / "defaults.yml")
        rules_configs = self._get_rules_files()
        enabled_rules, disabled_rules = self._partition_rules_disabled(rules_configs)
        defaults.update({"rules_disabled": disabled_rules, "rules": enabled_rules})
        return RulesConfig(iac=CategoryRuleConfig(**defaults))


if __name__ == "__main__":
    root_path = Path(__file__).parent.parent.resolve()
    config = RulesConfigGenerator(root_path / RULES_FOLDER).generate()
    print(json.dumps(asdict(config)))
