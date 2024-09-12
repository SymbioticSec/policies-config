"""Constants used in the scripts."""

from pathlib import Path

SCANNER_CONFIG_FILENAME = "scanner_config.yml"
RULES_FOLDER = "rules-config"
# Should be updated if this file is moved
ROOT_PATH = Path(__file__).parent.parent.parent.resolve()
