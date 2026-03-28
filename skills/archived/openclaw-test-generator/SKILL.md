# Test Auto Generator Skill

This skill provides automated test generation capabilities for Python code.

## Overview

The Auto Test Generator is a comprehensive testing framework that automatically generates test cases for functions and classes. It supports:

- Function signature-based test case generation
- Class testing (init, methods, properties)
- Edge case handling (boundary values, exceptions, None handling)
- Automatic Mock support for external dependencies
- One-click test execution with detailed reports

## Usage

When you need to generate automated tests for Python code, invoke this skill by describing what you want to test.

### Examples:
- "Generate tests for this function"
- "Write test cases for this class"
- "Create unit tests for my module"
- "Add edge case tests for the login function"

## Features

### 1. Function Test Generation
Analyzes function signatures and generates appropriate test cases:
- Normal input cases
- Type validation tests
- Return value verification

### 2. Class Testing
Tests class components:
- `__init__` method testing
- Public method testing
- Property testing
- Inheritance handling

### 3. Edge Cases
Comprehensive edge case coverage:
- Boundary values (min/max, empty/full)
- Exception handling
- None/NoneType handling
- Empty collections
- Invalid inputs

### 4. Mock Support
Automatic mocking for:
- External API calls
- File I/O operations
- Database connections
- Time/date functions
- Random number generators

### 5. Test Runner
One-click test execution with:
- Colored output
- Failure details
- Coverage reporting
- Summary statistics

## Integration

This skill works with the Open Claw agent to automatically generate and run tests for any Python code being developed.
