"""
Quick test script to verify logging and monitoring system setup
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import json
        print("✅ json")
    except ImportError as e:
        print(f"❌ json: {e}")
        return False
    
    try:
        import csv
        print("✅ csv")
    except ImportError as e:
        print(f"❌ csv: {e}")
        return False
    
    try:
        import matplotlib
        print(f"✅ matplotlib (version {matplotlib.__version__})")
    except ImportError as e:
        print(f"❌ matplotlib: {e}")
        print("   Install with: pip install matplotlib")
        return False
    
    try:
        import pandas as pd
        print(f"✅ pandas (version {pd.__version__})")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        print("   Install with: pip install pandas")
        return False
    
    try:
        from core.metrics_logger import MetricsLogger
        print("✅ core.metrics_logger")
    except ImportError as e:
        print(f"❌ core.metrics_logger: {e}")
        return False
    
    print("")
    return True


def test_logger():
    """Test basic logger functionality"""
    print("Testing logger functionality...")
    
    try:
        from core.metrics_logger import MetricsLogger
        
        # Create test logger
        logger = MetricsLogger(session_name="test_session", output_dir="test_logs")
        
        # Test logging various events
        logger.log_event("TEST_EVENT", {"test": "data"}, simulation_time=0.0)
        logger.log_dot_birth(1, 1, [], 100, 0.0)
        logger.log_attack(1, 2, 10.5, True, 1.0)
        logger.log_reproduction([1, 2], 3, 'sexual', 2.0)
        logger.log_dot_death(1, 'combat', 5.0)
        
        # Close logger
        logger.close()
        
        # Verify files were created
        test_dir = Path("test_logs/test_session")
        if test_dir.exists():
            files = list(test_dir.iterdir())
            print(f"✅ Created {len(files)} log files:")
            for f in files:
                print(f"   - {f.name}")
            
            # Cleanup
            import shutil
            shutil.rmtree("test_logs")
            print("✅ Test cleanup complete")
        else:
            print("❌ Test log directory not created")
            return False
        
        print("")
        return True
        
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 METRICS LOGGING SYSTEM TEST")
    print("=" * 60)
    print("")
    
    # Test imports
    if not test_imports():
        print("")
        print("❌ Import test failed!")
        print("Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        return False
    
    # Test logger
    if not test_logger():
        print("")
        print("❌ Logger test failed!")
        return False
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("")
    print("The logging and monitoring system is ready to use!")
    print("")
    print("Next steps:")
    print("1. Run the simulation: python main.py")
    print("2. In another terminal: python monitor.py")
    print("3. Watch the real-time dashboard!")
    print("")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
