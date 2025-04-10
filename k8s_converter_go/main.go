package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"

	"gopkg.in/yaml.v3"
)

func isValidYAML(data []byte) bool {
	var result map[string]interface{}
	err := yaml.Unmarshal(data, &result)
	return err == nil && len(result) > 0
}

func main() {
	// Define command line flags
	inputFile := flag.String("input", "", "Input YAML file path")
	outputFile := flag.String("output", "", "Output JSON file path (optional, will print to stdout if not specified)")
	flag.Parse()

	// Check if input file is provided
	if *inputFile == "" {
		fmt.Println("Error: Input file is required")
		fmt.Println("Usage: go run main.go -input <yaml-file> [-output <json-file>]")
		os.Exit(1)
	}

	// Check if file has .yaml or .yml extension
	if !strings.HasSuffix(strings.ToLower(*inputFile), ".yaml") && !strings.HasSuffix(strings.ToLower(*inputFile), ".yml") {
		fmt.Printf("Error: Input file '%s' does not have a .yaml or .yml extension\n", *inputFile)
		os.Exit(1)
	}

	// Read the input YAML file
	yamlData, err := os.ReadFile(*inputFile)
	if err != nil {
		fmt.Printf("Error reading input file: %v\n", err)
		os.Exit(1)
	}

	// Validate YAML content
	if !isValidYAML(yamlData) {
		fmt.Printf("Error: File '%s' contains invalid YAML content\n", *inputFile)
		os.Exit(1)
	}

	// Parse YAML into a generic map
	var data interface{}
	err = yaml.Unmarshal(yamlData, &data)
	if err != nil {
		fmt.Printf("Error parsing YAML: %v\n", err)
		os.Exit(1)
	}

	// Convert to JSON
	jsonData, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		fmt.Printf("Error converting to JSON: %v\n", err)
		os.Exit(1)
	}

	// Output the result
	if *outputFile != "" {
		// Write to output file
		err = os.WriteFile(*outputFile, jsonData, 0644)
		if err != nil {
			fmt.Printf("Error writing output file: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Successfully converted YAML to JSON and saved to %s\n", *outputFile)
	} else {
		// Print to stdout
		fmt.Println(string(jsonData))
	}
}
