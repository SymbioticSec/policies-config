# policies-config

This repository holds all configurations related to vulnerability scanners, and their policies.

## How to

### Update the scanner version

In the `scanner_config.yml` file:

- Set `scanner-version` to the scanner version to use. Refer to the [Trivy releases](https://github.com/aquasecurity/trivy/releases) to find a list of the existing versions.
- Set `rules-version` to the policy bundle version to use. Refer to the [Trivy-policies packages](https://github.com/aquasecurity/trivy-checks/pkgs/container/trivy-policies) for a list of possibilities. You can set the version to `0` to always use the latest, although it is not recommended. New changes introduced by a bundle version should be examined before they are accepted.

### Define the minimum severity

Set the minimum severity in `rules-config/iac/defaults.yml`. Choices are CRITICAL, HIGH, MEDIUM and LOW. Only vulnerabilities of severity equal or higher should be considered.

### Alter a policy

Create a YAML file in the correct subdirectory of `rules-config`, named with the original policy ID. For instance, `rules-config/iac/cloud/aws/AWS-AVD-0001.yml`.
Possible options in that file are:

- `disabled` (boolean, defaults to false): whether this policy should be ignored by the scanner.
- `severity` (CRITICAL, HIGH, MEDIUM or LOW, optional): when set, this overrides the severity defined by the scanner. The `minimum-severity` global setting must be applied **before** this one.

## Scripts

All scripts are automatically applied during CI, unless otherwise stated. They are available for manual use if necessary.
You'll need to install Python and its dependencies using [Poetry](https://python-poetry.org/docs/#installation).

- `poetry run python -m scripts.main generate-config`: Generates a single JSON grouping all configuration files. Note that `generate-rules-config` and `generate-scanner-config` can also be run individually. Example config:

```json
{
  "scanners": {
    "iac": {
      "scanner-version": "0.52.0",
      "rules-version": "0.11.0",
      "scanner-dl-links": {
        "windows": "https://...",
        "darwin_amd64": "https://...",
        "darwin_arm64": "https://...",
        "linux_amd64": "https://...",
        "linux_arm64": "https://..."
      }
    }
  },
  "rules": {
    "iac": {
      "minimum-severity": "MEDIUM",
      "rules_disabled": ["AWS-AVD-0002"],
      "rules": { "AWS-AVD-0001": { "severity": "HIGH" } }
    }
  }
}
```
