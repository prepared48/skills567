#!/usr/bin/env python3
"""
Find potential memory leaks in Java code.
Scans for common patterns that lead to memory leaks.
"""

import os
import re
from pathlib import Path

# Patterns to detect memory leaks
PATTERNS = [
    {
        'name': 'Unclosed InputStream',
        'pattern': r'(InputStream|FileInputStream|BufferedInputStream)\s+\w+\s*=\s*new\s+',
        'exclusion': r'try\s*\(\s*',
        'severity': 'CRITICAL',
        'description': 'InputStream not wrapped in try-with-resources',
    },
    {
        'name': 'Unclosed OutputStream',
        'pattern': r'(OutputStream|FileOutputStream|BufferedOutputStream)\s+\w+\s*=\s*new\s+',
        'exclusion': r'try\s*\(\s*',
        'severity': 'CRITICAL',
        'description': 'OutputStream not wrapped in try-with-resources',
    },
    {
        'name': 'Unclosed Reader/Writer',
        'pattern': r'(BufferedReader|BufferedWriter|FileReader|FileWriter)\s+\w+\s*=\s*new\s+',
        'exclusion': r'try\s*\(\s*',
        'severity': 'CRITICAL',
        'description': 'Reader/Writer not wrapped in try-with-resources',
    },
    {
        'name': 'Unclosed Connection',
        'pattern': r'Connection\s+\w+\s*=\s*[^;]*getConnection\(\)',
        'exclusion': r'try\s*\(\s*Connection',
        'severity': 'CRITICAL',
        'description': 'JDBC Connection not wrapped in try-with-resources',
    },
    {
        'name': 'Unclosed Statement',
        'pattern': r'(Statement|PreparedStatement)\s+\w+\s*=\s*[^;]*create',
        'exclusion': r'try\s*\(\s*(Statement|PreparedStatement)',
        'severity': 'CRITICAL',
        'description': 'JDBC Statement not wrapped in try-with-resources',
    },
    {
        'name': 'Unclosed ResultSet',
        'pattern': r'ResultSet\s+\w+\s*=\s*[^;]*execute',
        'exclusion': r'try\s*\(\s*ResultSet',
        'severity': 'CRITICAL',
        'description': 'JDBC ResultSet not wrapped in try-with-resources',
    },
    {
        'name': 'Static Collection',
        'pattern': r'(private|public|protected)\s+static\s+(Map|List|Set|Collection)\s+',
        'exclusion': r'(final|MAX_SIZE|MAX_COUNT)',
        'severity': 'HIGH',
        'description': 'Static collection may grow indefinitely',
    },
    {
        'name': 'Unclosed Socket',
        'pattern': r'Socket\s+\w+\s*=\s*new\s+',
        'exclusion': r'try\s*\(\s*Socket',
        'severity': 'CRITICAL',
        'description': 'Socket not wrapped in try-with-resources',
    },
    {
        'name': 'ThreadLocal without remove',
        'pattern': r'ThreadLocal<',
        'exclusion': r'remove\(\)',
        'severity': 'HIGH',
        'description': 'ThreadLocal may not be cleaned up',
    },
    {
        'name': 'ExecutorService without shutdown',
        'pattern': r'ExecutorService\s+\w+\s*=\s*',
        'exclusion': r'shutdown\(\)',
        'severity': 'HIGH',
        'description': 'ExecutorService may not have shutdown logic',
    },
    {
        'name': 'String concatenation in loop',
        'pattern': r'(for|while)\s*\([^)]*\)\s*\{[^}]*\+\s*=.*\+',
        'exclusion': r'StringBuilder|StringBuffer',
        'severity': 'MEDIUM',
        'description': 'String concatenation in loop - use StringBuilder',
    },
]


def check_file(filepath):
    """Check a single Java file for memory leak patterns."""
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
        issues.extend(file_issues)

    return issues


def print_issues(issues):
    """Print found issues in a readable format."""
    if not issues:
        print("\n✅ No memory leak issues found!")
        return

    # Sort by severity
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    issues.sort(key=lambda x: severity_order.get(x['severity'], 4))

    # Count by severity
    severity_counts = {}
    for issue in issues:
        severity_counts[issue['severity']] = severity_counts.get(issue['severity'], 0) + 1

    print("\n" + "=" * 80)
    print(f"MEMORY LEAK DETECTION RESULTS - {len(issues)} issues found")
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
        print(f"  Code: {issue['code'][:80]}...")

    print("\n" + "=" * 80)


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python find_memory_leaks.py <directory|file>")
        print("Example: python find_memory_leaks.py src/main/java")
        sys.exit(1)

    target = sys.argv[1]
    issues = []

    if os.path.isfile(target):
        print(f"Scanning file: {target}")
        issues = check_file(target)
    elif os.path.isdir(target):
        issues = scan_directory(target)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)

    print_issues(issues)


if __name__ == '__main__':
    main()
