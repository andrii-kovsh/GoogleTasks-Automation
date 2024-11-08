from google.auth.transport.requests import Request
import unittest
import sys
import Google_Tasks_Bot  # Import your main bot script here

# Function to run all unit tests
def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='.', pattern="Unit_Tests.py")
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    # Check if all tests were successful
    if result.wasSuccessful():
        print("All tests passed! Running the main script...")
        return True
    else:
        print("\nSome tests failed. Details below:")
        # Print failures and errors for debugging
        for failed_test, traceback in result.failures:
            print(f"\nFailed test: {failed_test.id()}")
            print(traceback)
        for error_test, traceback in result.errors:
            print(f"\nError in test: {error_test.id()}")
            print(traceback)
        return False

# Run the tests and, if successful, execute the main script
if __name__ == "__main__":
    if run_tests():
        Google_Tasks_Bot.main()  # Call the main function from Google_Tasks_Bot if tests pass
    else:
        print("Main script execution skipped due to test failures.")
        sys.exit(1)