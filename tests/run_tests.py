"""
Test runner for SMWCentral Downloader & Patcher
Runs all unit tests and generates coverage reports
"""
import unittest
import sys
import os
import time
from io import StringIO

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def run_all_tests(verbosity=2, coverage_enabled=True):
    """
    Run all tests with optional coverage reporting
    
    Args:
        verbosity (int): Test verbosity level (0-2)
        coverage_enabled (bool): Whether to generate coverage report
    
    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("🧪 SMWCentral Downloader & Patcher - Test Suite")
    print("=" * 60)
    
    # Initialize coverage if available and enabled
    cov = None
    if coverage_enabled:
        try:
            import coverage
            cov = coverage.Coverage(source=[PROJECT_ROOT])
            cov.start()
            print("📊 Coverage tracking enabled")
        except ImportError:
            print("⚠️  Coverage package not available. Install with: pip install coverage")
            coverage_enabled = False
    
    # Discover and run tests
    test_dir = os.path.dirname(__file__)
    loader = unittest.TestLoader()
    
    # Load all test modules
    test_modules = [
        'tests.test_utils',
        'tests.test_config_manager',
        'tests.test_hack_data_manager',
        'tests.test_api_pipeline',
        'tests.test_patch_handler',
        'tests.test_ui_components',
        'tests.test_integration'
    ]
    
    suite = unittest.TestSuite()
    
    print("🔍 Discovering tests...")
    test_count = 0
    
    for module_name in test_modules:
        try:
            module_suite = loader.loadTestsFromName(module_name)
            suite.addTest(module_suite)
            test_count += module_suite.countTestCases()
            print(f"   ✓ {module_name}: {module_suite.countTestCases()} tests")
        except Exception as e:
            print(f"   ❌ {module_name}: Failed to load ({e})")
    
    print(f"\n📋 Total tests found: {test_count}")
    print("=" * 60)
    
    # Run tests
    start_time = time.time()
    
    # Capture test output
    test_output = StringIO()
    runner = unittest.TextTestRunner(
        stream=test_output,
        verbosity=verbosity,
        buffer=True
    )
    
    result = runner.run(suite)
    end_time = time.time()
    
    # Print results
    print("📊 Test Results:")
    print("=" * 60)
    
    print(f"⏱️  Execution time: {end_time - start_time:.2f} seconds")
    print(f"🧪 Tests run: {result.testsRun}")
    print(f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        print(f"❌ Failures: {len(result.failures)}")
        for test, traceback in result.failures:
            last_line = traceback.split('\n')[-2] if traceback else 'Unknown failure'
            print(f"   • {test}: {last_line}")
    
    if result.errors:
        print(f"💥 Errors: {len(result.errors)}")
        for test, traceback in result.errors:
            last_line = traceback.split('\n')[-2] if traceback else 'Unknown error'
            print(f"   • {test}: {last_line}")
    
    if result.skipped:
        print(f"⏭️  Skipped: {len(result.skipped)}")
        for test, reason in result.skipped:
            print(f"   • {test}: {reason}")
    
    # Calculate success rate
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    # Generate coverage report
    if coverage_enabled and cov:
        print("\\n📊 Coverage Report:")
        print("=" * 60)
        
        try:
            cov.stop()
            cov.save()
            
            # Print coverage report to console
            print("Coverage by module:")
            coverage_data = cov.get_data()
            
            # Get coverage summary
            total_lines = 0
            covered_lines = 0
            
            for filename in coverage_data.measured_files():
                if PROJECT_ROOT in filename and not filename.endswith('test_'):
                    relative_path = os.path.relpath(filename, PROJECT_ROOT)
                    lines = coverage_data.lines(filename)
                    missing = coverage_data.missing(filename)
                    
                    if lines:
                        total_lines += len(lines)
                        covered_lines += len(lines) - len(missing)
                        coverage_percent = ((len(lines) - len(missing)) / len(lines)) * 100
                        print(f"   {relative_path}: {coverage_percent:.1f}% ({len(lines) - len(missing)}/{len(lines)} lines)")
            
            if total_lines > 0:
                overall_coverage = (covered_lines / total_lines) * 100
                print(f"\\n🎯 Overall coverage: {overall_coverage:.1f}% ({covered_lines}/{total_lines} lines)")
                
                if overall_coverage >= 80:
                    print("🎉 Excellent! Coverage target (80%) achieved!")
                elif overall_coverage >= 70:
                    print("👍 Good coverage! Close to 80% target.")
                else:
                    print("⚠️  Coverage below 70%. Consider adding more tests.")
            
            # Generate HTML report
            html_report_dir = os.path.join(PROJECT_ROOT, "coverage_html")
            cov.html_report(directory=html_report_dir)
            print(f"\\n📄 HTML coverage report generated: {html_report_dir}/index.html")
            
        except Exception as e:
            print(f"❌ Error generating coverage report: {e}")
    
    print("\\n" + "=" * 60)
    
    # Final result
    if result.wasSuccessful():
        print("🎉 All tests passed! ✨")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False

def run_specific_test(test_module, test_class=None, test_method=None):
    """
    Run a specific test module, class, or method
    
    Args:
        test_module (str): Module name (e.g., 'test_utils')
        test_class (str, optional): Test class name
        test_method (str, optional): Test method name
    """
    test_name = f"tests.{test_module}"
    if test_class:
        test_name += f".{test_class}"
        if test_method:
            test_name += f".{test_method}"
    
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main test runner entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SMWCentral Downloader & Patcher Test Runner")
    parser.add_argument("--module", "-m", help="Run specific test module")
    parser.add_argument("--class", "-c", dest="test_class", help="Run specific test class")
    parser.add_argument("--method", "-t", dest="test_method", help="Run specific test method")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--verbose", "-v", action="count", default=1, help="Increase verbosity")
    
    args = parser.parse_args()
    
    if args.module:
        success = run_specific_test(args.module, args.test_class, args.test_method)
    else:
        success = run_all_tests(
            verbosity=min(args.verbose, 2),
            coverage_enabled=not args.no_coverage
        )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
