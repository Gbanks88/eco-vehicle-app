#!/usr/bin/env python3

import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Tuple

class TestReportGenerator:
    def __init__(self):
        self.template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Complex Systems Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #f8f9fa; padding: 20px; border-radius: 5px; }
                .summary { margin: 20px 0; }
                .metric { background: #fff; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .success { color: #28a745; }
                .warning { color: #ffc107; }
                .failure { color: #dc3545; }
                .details { margin: 20px 0; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
                th { background: #f8f9fa; }
                .performance-chart { margin: 20px 0; }
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """

    def parse_test_results(self, results_file: Path) -> Dict:
        """Parse JUnit XML test results"""
        tree = ET.parse(results_file)
        root = tree.getroot()
        
        results = {
            'total': 0,
            'failures': 0,
            'errors': 0,
            'skipped': 0,
            'time': 0.0,
            'test_cases': []
        }
        
        for testsuite in root.findall('.//testsuite'):
            results['total'] += int(testsuite.get('tests', 0))
            results['failures'] += int(testsuite.get('failures', 0))
            results['errors'] += int(testsuite.get('errors', 0))
            results['skipped'] += int(testsuite.get('skipped', 0))
            results['time'] += float(testsuite.get('time', 0))
            
            for testcase in testsuite.findall('testcase'):
                case = {
                    'name': testcase.get('name'),
                    'class': testcase.get('classname'),
                    'time': float(testcase.get('time', 0)),
                    'status': 'passed'
                }
                
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped = testcase.find('skipped')
                
                if failure is not None:
                    case['status'] = 'failed'
                    case['message'] = failure.get('message')
                elif error is not None:
                    case['status'] = 'error'
                    case['message'] = error.get('message')
                elif skipped is not None:
                    case['status'] = 'skipped'
                    case['message'] = skipped.get('message')
                
                results['test_cases'].append(case)
        
        return results

    def parse_coverage(self, coverage_file: Path) -> Dict:
        """Parse coverage XML report"""
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        coverage = {
            'line_rate': float(root.get('line-rate', 0)) * 100,
            'branch_rate': float(root.get('branch-rate', 0)) * 100,
            'complexity': float(root.get('complexity', 0)),
            'packages': []
        }
        
        for package in root.findall('.//package'):
            pkg = {
                'name': package.get('name'),
                'line_rate': float(package.get('line-rate', 0)) * 100,
                'branch_rate': float(package.get('branch-rate', 0)) * 100,
                'complexity': float(package.get('complexity', 0))
            }
            coverage['packages'].append(pkg)
        
        return coverage

    def generate_summary_section(self, unit_results: Dict, integration_results: Dict,
                               performance_results: Dict, validation_results: Dict,
                               coverage: Dict) -> str:
        """Generate HTML summary section"""
        total_tests = (unit_results['total'] + integration_results['total'] +
                      performance_results['total'] + validation_results['total'])
        total_failures = (unit_results['failures'] + integration_results['failures'] +
                         performance_results['failures'] + validation_results['failures'])
        
        status_class = 'success' if total_failures == 0 else 'failure'
        coverage_class = 'success' if coverage['line_rate'] >= 80 else 'warning'
        
        return f"""
        <div class="header">
            <h1>Complex Systems Test Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="metric">
                <h3 class="{status_class}">Overall Status: {'PASS' if total_failures == 0 else 'FAIL'}</h3>
                <p>Total Tests: {total_tests}</p>
                <p>Total Failures: {total_failures}</p>
                <p class="{coverage_class}">Code Coverage: {coverage['line_rate']:.2f}%</p>
            </div>
        </div>
        """

    def generate_test_section(self, title: str, results: Dict) -> str:
        """Generate HTML section for test results"""
        status_class = 'success' if results['failures'] == 0 else 'failure'
        
        return f"""
        <div class="details">
            <h2>{title}</h2>
            <div class="metric">
                <h3 class="{status_class}">Status: {'PASS' if results['failures'] == 0 else 'FAIL'}</h3>
                <p>Total Tests: {results['total']}</p>
                <p>Failures: {results['failures']}</p>
                <p>Errors: {results['errors']}</p>
                <p>Skipped: {results['skipped']}</p>
                <p>Time: {results['time']:.2f}s</p>
            </div>
            
            <table>
                <tr>
                    <th>Test Case</th>
                    <th>Status</th>
                    <th>Time (s)</th>
                    <th>Message</th>
                </tr>
                {''.join(
                    f"<tr><td>{case['name']}</td>"
                    f"<td class='{case['status']}'>{case['status'].upper()}</td>"
                    f"<td>{case['time']:.3f}</td>"
                    f"<td>{case.get('message', '')}</td></tr>"
                    for case in results['test_cases']
                )}
            </table>
        </div>
        """

    def generate_coverage_section(self, coverage: Dict) -> str:
        """Generate HTML section for coverage results"""
        return f"""
        <div class="details">
            <h2>Coverage Details</h2>
            <div class="metric">
                <p>Line Coverage: {coverage['line_rate']:.2f}%</p>
                <p>Branch Coverage: {coverage['branch_rate']:.2f}%</p>
                <p>Complexity: {coverage['complexity']:.2f}</p>
            </div>
            
            <table>
                <tr>
                    <th>Package</th>
                    <th>Line Coverage</th>
                    <th>Branch Coverage</th>
                    <th>Complexity</th>
                </tr>
                {''.join(
                    f"<tr><td>{pkg['name']}</td>"
                    f"<td>{pkg['line_rate']:.2f}%</td>"
                    f"<td>{pkg['branch_rate']:.2f}%</td>"
                    f"<td>{pkg['complexity']:.2f}</td></tr>"
                    for pkg in coverage['packages']
                )}
            </table>
        </div>
        """

    def generate_report(self, unit_results: Path, integration_results: Path,
                       performance_results: Path, validation_results: Path,
                       coverage_file: Path, output_file: Path):
        """Generate complete HTML test report"""
        unit = self.parse_test_results(unit_results)
        integration = self.parse_test_results(integration_results)
        performance = self.parse_test_results(performance_results)
        validation = self.parse_test_results(validation_results)
        coverage = self.parse_coverage(coverage_file)
        
        content = (
            self.generate_summary_section(unit, integration, performance, validation, coverage) +
            self.generate_test_section("Unit Tests", unit) +
            self.generate_test_section("Integration Tests", integration) +
            self.generate_test_section("Performance Tests", performance) +
            self.generate_test_section("Validation Tests", validation) +
            self.generate_coverage_section(coverage)
        )
        
        report = self.template.format(content=content)
        
        with open(output_file, 'w') as f:
            f.write(report)

def main():
    parser = argparse.ArgumentParser(description='Generate comprehensive test report')
    parser.add_argument('--unit-results', required=True, help='Unit test results XML file')
    parser.add_argument('--integration-results', required=True, help='Integration test results XML file')
    parser.add_argument('--performance-results', required=True, help='Performance test results XML file')
    parser.add_argument('--validation-results', required=True, help='Validation test results XML file')
    parser.add_argument('--unit-coverage', required=True, help='Coverage XML file')
    parser.add_argument('--output', required=True, help='Output HTML report file')
    
    args = parser.parse_args()
    
    generator = TestReportGenerator()
    generator.generate_report(
        Path(args.unit_results),
        Path(args.integration_results),
        Path(args.performance_results),
        Path(args.validation_results),
        Path(args.unit_coverage),
        Path(args.output)
    )

if __name__ == '__main__':
    main()
