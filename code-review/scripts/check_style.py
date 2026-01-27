#!/usr/bin/env python3
"""
Check Java code style issues based on Alibaba Java Coding Guidelines.
"""

import os
import re
from pathlib import Path

# Patterns to detect style issues
PATTERNS = [
    {
        'name': 'Magic Number',
        'pattern': r'(return|if|while|for|==|!=|<|>|<=|>=)\s+[\d]+[^\d;]',
        'exclusion': r'(//|\*)',
        'severity': 'MEDIUM',
        'description': 'Magic number without constant definition',
    },
    {
        'name': 'String concatenation in log',
        'pattern': r'(log\.(info|debug|warn|error|trace)\s*\(\s*"[^"]*\s*\+\s*',
        'exclusion': None,
        'severity': 'MEDIUM',
        'description': 'String concatenation in log call - use parameterized logging',
    },
    {
        'name': 'Broad exception catch',
        'pattern': r'catch\s*\(\s*Exception\s+\w+\s*\)',
        'exclusion': None,
        'severity': 'HIGH',
        'description': 'Catching broad Exception - catch specific exceptions',
    },
    {
        'name': 'Print stack trace',
        'pattern': r'\.printStackTrace\(\)',
        'exclusion': r'//',
        'severity': 'HIGH',
        'description': 'Using printStackTrace() - use logger',
    },
    {
        'name': 'Empty catch block',
        'pattern': r'catch\s*\([^)]*\)\s*\{\s*\}',
        'exclusion': r'//',
        'severity': 'HIGH',
        'description': 'Empty catch block - log or handle exception',
    },
    {
        'name': 'Return null in catch',
        'pattern': r'catch\s*\([^)]*\)\s*\{[^}]*return\s+null',
        'exclusion': r'//',
        'severity': 'MEDIUM',
        'description': 'Returning null in catch block - throw exception or return default',
    },
    {
        'name': 'Hardcoded password',
        'pattern': r'(password|pwd|secret)\s*=\s*"[^"]+"',
        'exclusion': r'(//|// TODO|FIXME)',
        'severity': 'CRITICAL',
        'description': 'Hardcoded password or secret',
    },
    {
        'name': 'System.out.println',
        'pattern': r'System\.out\.println\(',
        'exclusion': r'(//|// TODO|FIXME)',
        'severity': 'MEDIUM',
        'description': 'Using System.out.println - use logger',
    },
    {
        'name': 'System.err.println',
        'pattern': r'System\.err\.println\(',
        'exclusion': r'(//|// TODO|FIXME)',
        'severity': 'MEDIUM',
        'description': 'Using System.err.println - use logger',
    },
    {
        'name': 'String comparison with ==',
        'pattern': r'(String\s+\w+)\s*==\s*',
        'exclusion': r'(//|// TODO|FIXME)',
        'severity': 'MEDIUM',
        'description': 'String comparison with == - use equals()',
    },
    {
        'name': 'Long method (potential)',
        'pattern': r'public\s+(?!class|interface|enum)[^{]+\{.*\{.*\{.*\{',
        'exclusion': None,
        'severity': 'LOW',
        'description': 'Method with deep nesting - consider refactoring',
    },
    {
        'name': 'TODO without owner',
        'pattern': r'TODO(?!:)',
        'exclusion': r'TODO:\s*\w+:',
        'severity': 'LOW',
        'description': 'TODO without owner and date',
    },
    {
        'name': 'SQL injection risk (string concat)',
        'pattern': r'(SELECT|INSERT|UPDATE|DELETE)\s+[^;]*\s*\+\s*\w+',
        'exclusion': r'(//|\*)',
        'severity': 'CRITICAL',
        'description': 'SQL query with string concatenation - use parameterized queries',
    },
    {
        'name': 'Empty line count',
        'pattern': r'\n\s*\n\s*\n',
        'exclusion': None,
        'severity': 'LOW',
        'description': 'Multiple empty lines - remove extra blank lines',
    },
    {
        'name': 'Trailing whitespace',
        'pattern': r'[ \t]+\n',
        'exclusion': None,
        'severity': 'LOW',
        'description': 'Trailing whitespace - remove spaces at end of line',
    },
    {
        'name': 'Star import',
        'pattern': r'^import\s+[\w.]+\.(\*|\*)\s*;',
        'exclusion': None,
        'severity': 'MEDIUM',
        'description': 'Star import - import specific classes',
    },
]


def check_file(filepath):
    """Check a single Java file for style issues."""
    issues = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

            for pattern_def in PATTERNS:
                pattern = pattern_def['pattern']
                exclusion = pattern_def.get('exclusion', '')

                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        # Check for exclusion
                        if exclusion and re.search(exclusion, line):
                            continue

                        issues.append({
                            'line': line_num,
                            'file': filepath,
                            'severity': pattern_def['severity'],
                            'name': pattern_def['name'],
                            'description': pattern_def['description'],
                            'code': line.strip(),
                        })
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return issues


def check_complexity(filepath):
    """Check cyclomatic complexity of methods."""
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

            in_method = False
            method_start = 0
            brace_count = 0
            complexity = 1

            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()

                # Detect method start
                if re.match(r'(public|private|protected|static|final)?\s*(\w+<[^>]*>)?\s+\w+\s*\([^)]*\)\s*(throws\s+[\w\s,]+)?\s*\{', stripped):
                    if not in_method:
                        in_method = True
                        method_start = line_num
                        brace_count = 1
                        complexity = 1
                    continue

                if in_method:
                    # Count braces
                    brace_count += stripped.count('{')
                    brace_count -= stripped.count('}')

                    # Count complexity points
                    if re.search(r'\b(if|else|case|default|for|while|catch|switch)\b', stripped):
                        complexity += 1

                    # Method end
                    if brace_count == 0:
                        in_method = False
                        if complexity > 10:
                            issues.append({
                                'line': method_start,
                                'file': filepath,
                                'severity': 'MEDIUM',
                                'name': 'High Cyclomatic Complexity',
                                'description': f'Method has complexity {complexity} (recommended: < 10)',
                                'code': lines[method_start - 1].strip()[:80],
                            })
                        complexity = 1

    except Exception as e:
        print(f"Error analyzing complexity for {filepath}: {e}")

    return issues


def scan_directory(directory):
    """Scan all Java files in directory recursively."""
    issues = []
    java_files = list(Path(directory).rglob('*.java'))

    if not java_files:
        print(f"No Java files found in {directory}")
        return issues

    print(f"Scanning {len(java_files)} Java files...")

    for filepath in java_files:
        file_issues = check_file(str(filepath))
        complexity_issues = check_complexity(str(filepath))
        issues.extend(file_issues)
        issues.extend(complexity_issues)

    return issues


def print_issues(issues):
    """Print found issues in a readable format."""
    if not issues:
        print("\n✅ No style issues found!")
        return

    # Sort by severity
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    issues.sort(key=lambda x: severity_order.get(x['severity'], 4))

    # Count by severity
    severity_counts = {}
    for issue in issues:
        severity_counts[issue['severity']] = severity_counts.get(issue['severity'], 0) + 1

    print("\n" + "=" * 80)
    print(f"STYLE CHECK RESULTS - {len(issues)} issues found")
    print("=" * 80)

    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = severity_counts.get(severity, 0)
        if count > 0:
            print(f"\n[{severity}]: {count} issue(s)")

    print("\n" + "-" * 80)
    for issue in issues:
        print(f"\n[{issue['severity']}] {issue['name']}")
        print(f"  File: {issue['file']}:{issue['line']}")
        print(f"  Description: {issue['description']}")
        if 'code' in issue and issue['code']:
            print(f"  Code: {issue['code'][:80]}...")

    print("\n" + "=" * 80)


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python check_style.py <directory|file>")
        print("Example: python check_style.py src/main/java")
        sys.exit(1)

    target = sys.argv[1]
    issues = []

    if os.path.isfile(target):
        print(f"Scanning file: {target}")
        style_issues = check_file(target)
        complexity_issues = check_complexity(target)
        issues.extend(style_issues)
        issues.extend(complexity_issues)
    elif os.path.isdir(target):
        issues = scan_directory(target)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)

    print_issues(issues)


if __name__ == '__main__':
    main()
