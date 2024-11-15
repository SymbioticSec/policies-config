# policies-config

This repository holds all configurations related to vulnerability scanners, and their policies.

## How to

### Update the scanner version

In the `scanner_config.yml` file:

- Set `scanner-version` to the scanner version to use. Refer to the [Trivy releases](https://github.com/aquasecurity/trivy/releases) to find a list of the existing versions.
- Set `trivy-checks-version` to the policy bundle version to use. Refer to the [Trivy-checks releases](https://github.com/aquasecurity/trivy-checks/releases) for a list of possibilities.

### Define the minimum severity

Set the minimum severity in `rules-config/iac/defaults.yml`. Choices are CRITICAL, HIGH, MEDIUM and LOW. Only vulnerabilities of severity equal or higher should be considered.

### Alter a policy

Create a YAML file in the correct subdirectory of `rules-config`, named with the original policy ID. For instance, `rules-config/iac/cloud/aws/AWS-AVD-0001.yml`.
Possible options in that file are:

- `disabled` (boolean, defaults to false): whether this policy should be ignored by the scanner.
- `severity` (CRITICAL, HIGH, MEDIUM or LOW, optional): when set, this overrides the severity defined by the scanner. The `minimum-severity` global setting must be applied **before** this one.

## Scripts

You'll need to install Python and its dependencies using [Poetry](https://python-poetry.org/docs/#installation).

**The following scripts are automatically applied during CI, but are available for manual use.**

- `poetry run python -m scripts.main download-scanners`: Downloads the Trivy scanner releases for all supported system. Extracts the scanner binary from each archive. Call `clear-scanners` to remove all generated files.

- `poetry run python -m scripts.main generate-config`: Generates a single JSON grouping all configuration files. Note that `generate-rules-config` and `generate-scanner-config` can also be run individually. Example config:

```json
{
  "scanners": {
    "iac": {
      "scanner_version": "0.52.0",
      "trivy_checks_version": "v1.0.1",
      "scanner_dl_links": {
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
      "minimum_severity": "MEDIUM",
      "rules_disabled": ["AWS-AVD-0002"],
      "rules": { "AWS-AVD-0001": { "severity": "HIGH" } }
    }
  }
}
```

**The following scripts are available for manual use.**

- `poetry run python -m scripts.main generate-static-data <path>`: Generates static data for all policies in the given directory. More information in the [static data README](scripts/generate_static_data/README.md).
