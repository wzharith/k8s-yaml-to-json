package main

import (
	"os"
	"testing"
)

func TestNonYAMLInput(t *testing.T) {
	// Test cases
	tests := []struct {
		name        string
		content     []byte
		extension   string
		expectError bool
	}{
		{
			name:        "Plain text with .txt extension",
			content:     []byte("This is not a YAML file\nIt's just plain text"),
			extension:   ".txt",
			expectError: true,
		},
		{
			name:        "Invalid YAML with .yaml extension",
			content:     []byte("This is not valid: YAML: content"),
			extension:   ".yaml",
			expectError: true,
		},
		{
			name:        "Empty YAML with .yaml extension",
			content:     []byte(""),
			extension:   ".yaml",
			expectError: true,
		},
		{
			name:        "Valid YAML with .yaml extension",
			content:     []byte("apiVersion: v1\nkind: Pod\nmetadata:\n  name: test-pod"),
			extension:   ".yaml",
			expectError: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create temporary file
			tempFile, err := os.CreateTemp("", "test-*"+tt.extension)
			if err != nil {
				t.Fatalf("Failed to create temp file: %v", err)
			}
			defer os.Remove(tempFile.Name())

			// Write content
			if err := os.WriteFile(tempFile.Name(), tt.content, 0644); err != nil {
				t.Fatalf("Failed to write content: %v", err)
			}

			// Test YAML validation
			isValid := isValidYAML(tt.content)
			if isValid == tt.expectError {
				t.Errorf("isValidYAML() = %v, want %v for content: %s", isValid, !tt.expectError, string(tt.content))
			}
		})
	}
}
