package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"strings"
)

// RuleData represents the extracted data from scan.Rule
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

		key := kv.Key.(*ast.Ident).Name
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
			rule.Severity = getIdentifierOrString(kv.Value, "severity.", "")
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
				if typ.X.(*ast.Ident).Name == "scan" && typ.Sel.Name == "Rule" {
					rules = append(rules, parseRule(compLit))
				}
			}
		}
		return true
	})

	return rules, nil
}

// walkDirectories traverses the folder structure and processes each Go file
func walkDirectories(root string) ([]RuleData, error) {
	var allRules []RuleData

	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		// Process only Go files
		if !info.IsDir() && strings.HasSuffix(path, ".go") {
			rules, err := parseFile(path)
			if err != nil {
				return err
			}
			allRules = append(allRules, rules...)
		}
		return nil
	})

	return allRules, err
}

func main() {
	// Check if the user has passed a directory path
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run script.go <directory_path>")
		return
	}

	// Get the directory path from the first command-line argument
	rootDir := os.Args[1]

	// Walk through the directories and gather all scan.Rules
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