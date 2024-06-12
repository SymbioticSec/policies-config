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
