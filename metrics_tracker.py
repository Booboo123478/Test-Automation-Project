#!/usr/bin/env python

import subprocess
import json
import time
import re
from pathlib import Path


def main():
    start_time = time.time()
    
    # Run pytest with coverage
    result = subprocess.run(
        ['pytest', '--cov=core', '--cov-report=json', '-v'],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    
    execution_time = time.time() - start_time
    
    # Parse coverage
    coverage_pct = 0
    try:
        with open('coverage.json', 'r') as f:
            coverage_data = json.load(f)
            coverage_pct = coverage_data['totals']['percent_covered']
    except:
        pass
    
    # Parse test results from output
    output = result.stdout + result.stderr
    passed = failed = 0

    match = re.search(r'(\d+) passed', output)
    if match:
        passed = int(match.group(1))
    
    match = re.search(r'(\d+) failed', output)
    if match:
        failed = int(match.group(1))
    
    total = passed + failed
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # Count defects
    defects = failed
    
    # Display
    print(f"Code coverage: {coverage_pct:.1f}%")
    print(f"Test execution time: {execution_time:.2f}s")
    print(f"Pass/fail rate: {pass_rate:.1f}% ({passed}/{total} passed)")
    print(f"Defects found: {defects}")


if __name__ == '__main__':
    main()
