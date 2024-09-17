package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"strings"
)

// RuleData represents the extracted data from scan.Rule or Rego METADATA
type RuleData struct {
	AVDID       string `json:"AVDID"`
	Provider    string `json:"Provider"`
	Service     string `json:"Service"`
	ShortCode   string `json:"ShortCode"`
	Summary     string `json:"Summary"`
	Impact      string `json:"Impact"`
	Resolution  string `json:"Resolution"`
	Explanation string `json:"Explanation"`
	Severity    string `json:"Severity"`
	Deprecated  bool   `json:"Deprecated"`
}

// parseRule parses the *ast.CompositeLit representing scan.Rule and extracts relevant fields
func parseRule(node *ast.CompositeLit) RuleData {
	rule := RuleData{}

	for _, elt := range node.Elts {
		kv, ok := elt.(*ast.KeyValueExpr)
		if !ok {
			continue
		}

		key := ""
		switch k := kv.Key.(type) {
		case *ast.Ident:
			key = k.Name
		default:
			continue
		}

		switch key {
		case "AVDID":
			rule.AVDID = getStringValue(kv.Value)
		case "Provider":
			rule.Provider = getIdentifierOrString(kv.Value, "providers.", "Provider")
		case "Service":
			rule.Service = getStringValue(kv.Value)
		case "ShortCode":
			rule.ShortCode = getStringValue(kv.Value)
		case "Summary":
			rule.Summary = getStringValue(kv.Value)
		case "Impact":
			rule.Impact = getStringValue(kv.Value)
		case "Resolution":
			rule.Resolution = getStringValue(kv.Value)
		case "Explanation":
			rule.Explanation = getStringValue(kv.Value)
		case "Severity":
			rule.Severity = normalizeSeverity(getIdentifierOrString(kv.Value, "severity.", ""))
		case "Deprecated":
			rule.Deprecated = getBoolValue(kv.Value)
		}
	}

	return rule
}

// getStringValue extracts the string value from an ast.Expr
func getStringValue(expr ast.Expr) string {
	switch v := expr.(type) {
	case *ast.BasicLit:
		return strings.Trim(v.Value, `"`)
	}
	return ""
}

// getIdentifierOrString handles both string literals and identifiers like constants.
// It also removes the provided prefix and suffix if present.
func getIdentifierOrString(expr ast.Expr, prefixToRemove, suffixToRemove string) string {
	switch v := expr.(type) {
	case *ast.BasicLit:
		return strings.Trim(v.Value, `"`)
	case *ast.SelectorExpr:
		// Handle constants like providers.AWSProvider or severity.High
		value := fmt.Sprintf("%s.%s", v.X.(*ast.Ident).Name, v.Sel.Name)
		// Remove prefix if specified
		if prefixToRemove != "" {
			value = strings.TrimPrefix(value, prefixToRemove)
		}
		// Remove suffix if specified
		if suffixToRemove != "" {
			value = strings.TrimSuffix(value, suffixToRemove)
		}
		return value
	}
	return ""
}

// getBoolValue extracts the boolean value from an ast.Expr
func getBoolValue(expr ast.Expr) bool {
	switch v := expr.(type) {
	case *ast.Ident:
		return v.Name == "true"
	}
	return false
}

// normalizeSeverity normalizes severity strings to have the first letter capitalized
func normalizeSeverity(sev string) string {
	return strings.Title(strings.ToLower(sev))
}

// parseFile parses a Go source file and extracts scan.Rule definitions
func parseFile(filename string) ([]RuleData, error) {
	fset := token.NewFileSet()
	node, err := parser.ParseFile(fset, filename, nil, 0)
	if err != nil {
		return nil, err
	}

	var rules []RuleData

	// Inspect the AST and look for assignments to scan.Rule
	ast.Inspect(node, func(n ast.Node) bool {
		// Look for composite literals, like scan.Rule{...}
		if compLit, ok := n.(*ast.CompositeLit); ok {
			// Check if it's part of a scan.Rule assignment
			if typ, ok := compLit.Type.(*ast.SelectorExpr); ok {
				if ident, ok := typ.X.(*ast.Ident); ok && ident.Name == "scan" && typ.Sel.Name == "Rule" {
					rules = append(rules, parseRule(compLit))
				}
			}
		}
		return true
	})

	return rules, nil
}

// parseRegoFile parses a Rego file and extracts METADATA into RuleData
func parseRegoFile(filename string) ([]RuleData, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var rules []RuleData
	scanner := bufio.NewScanner(file)
	inMetadata := false
	metadata := make(map[string]string)
	var multilineKey string
	var multilineValue []string

	for scanner.Scan() {
		line := scanner.Text()
		trimmed := strings.TrimSpace(line)

		// Check for the start of METADATA
		if !inMetadata && strings.HasPrefix(trimmed, "# METADATA") {
			inMetadata = true
			continue
		}

		if inMetadata {
			if !strings.HasPrefix(trimmed, "#") {
				// End of METADATA section
				break
			}

			// Remove the leading '# ' or '#' from the line
			lineContent := strings.TrimPrefix(trimmed, "#")
			lineContent = strings.TrimSpace(lineContent)

			if multilineKey != "" {
				// Continue collecting multiline value
				if strings.HasPrefix(lineContent, "|") {
					// Description starts with '|', continue
					continue
				} else if strings.HasPrefix(lineContent, "-") || strings.Contains(lineContent, ":") {
					// Next key starts, save the current multiline
					metadata[multilineKey] = strings.Join(multilineValue, "\n")
					multilineKey = ""
					multilineValue = nil
				} else {
					// Collect multiline content
					multilineValue = append(multilineValue, strings.TrimSpace(lineContent))
					continue
				}
			}

			// Parse key: value
			if strings.Contains(lineContent, ":") {
				parts := strings.SplitN(lineContent, ":", 2)
				key := strings.TrimSpace(parts[0])
				value := strings.TrimSpace(parts[1])

				if strings.HasSuffix(value, "|") {
					// Start of multiline value
					multilineKey = key
					multilineValue = []string{}
					continue
				}

				// Remove surrounding quotes if present
				value = strings.Trim(value, `"'`)

				metadata[key] = value
			}
		}
	}

	// Handle any remaining multiline value
	if multilineKey != "" && len(multilineValue) > 0 {
		metadata[multilineKey] = strings.Join(multilineValue, "\n")
	}

	// Map metadata to RuleData
	rule := RuleData{}

	if val, ok := metadata["avd_id"]; ok {
		rule.AVDID = val
	}
	if val, ok := metadata["provider"]; ok {
		rule.Provider = val
	}
	if val, ok := metadata["service"]; ok {
		rule.Service = val
	}
	if val, ok := metadata["short_code"]; ok {
		rule.ShortCode = val
	}
	if val, ok := metadata["title"]; ok {
		rule.Summary = val
	}
	if val, ok := metadata["recommended_action"]; ok {
		rule.Resolution = val
	}
	if val, ok := metadata["description"]; ok {
		rule.Explanation = val
	}
	if val, ok := metadata["severity"]; ok {
		rule.Severity = normalizeSeverity(val)
	}

	// Only add rule if AVDID is present
	if rule.AVDID != "" {
		rules = append(rules, rule)
	}

	return rules, nil
}

// walkDirectories traverses the folder structure and processes each Go and Rego file
func walkDirectories(root string) ([]RuleData, error) {
	ruleMap := make(map[string]RuleData) // Keyed by AVDID

	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		// Process only Go and Rego files
		if !info.IsDir() {
			if strings.HasSuffix(path, ".go") {
				rules, err := parseFile(path)
				if err != nil {
					return fmt.Errorf("error parsing Go file %s: %v", path, err)
				}
				for _, rule := range rules {
					ruleMap[rule.AVDID] = rule // Go rules take precedence
				}
			} else if strings.HasSuffix(path, ".rego") {
				rules, err := parseRegoFile(path)
				if err != nil {
					return fmt.Errorf("error parsing Rego file %s: %v", path, err)
				}
				for _, rule := range rules {
					// Only add if AVDID not already present (Go takes precedence)
					if _, exists := ruleMap[rule.AVDID]; !exists {
						ruleMap[rule.AVDID] = rule
					}
				}
			}
		}
		return nil
	})

	if err != nil {
		return nil, err
	}

	// Convert map to slice
	var allRules []RuleData
	for _, rule := range ruleMap {
		allRules = append(allRules, rule)
	}

	return allRules, nil
}

func main() {
	// Check if the user has passed a directory path
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run script.go <directory_path>")
		return
	}

	// Get the directory path from the first command-line argument
	rootDir := os.Args[1]

	// Walk through the directories and gather all scan.Rules and Rego METADATA
	rules, err := walkDirectories(rootDir)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	// Convert the gathered rules to JSON format
	rulesJSON, err := json.MarshalIndent(rules, "", "  ")
	if err != nil {
		fmt.Println("Error marshaling to JSON:", err)
		return
	}

	// Print the JSON output
	fmt.Println(string(rulesJSON))
}
