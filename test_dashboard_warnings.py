#!/usr/bin/env python3
"""
Test script to verify that Dashboard warnings are fixed
"""

def test_dashboard_no_warnings():
    """Test that HackDataManager no longer produces duplicate warnings"""
    from hack_data_manager import HackDataManager
    import io
    import sys
    from contextlib import redirect_stdout
    
    print("🧪 Testing HackDataManager for duplicate warnings...")
    
    # Capture output to check for warnings
    captured_output = io.StringIO()
    
    try:
        with redirect_stdout(captured_output):
            # Initialize HackDataManager (this loads processed.json)
            data_manager = HackDataManager()
            
            # Test both include_obsolete modes
            print("Testing include_obsolete=False...")
            current_hacks = data_manager.get_all_hacks(include_obsolete=False)
            
            print("Testing include_obsolete=True...")
            all_hacks = data_manager.get_all_hacks(include_obsolete=True)
        
        # Check captured output for warnings
        output = captured_output.getvalue()
        warnings = [line for line in output.split('\n') if 'WARNING: Duplicate title' in line]
        
        if warnings:
            print(f"❌ Found {len(warnings)} warnings:")
            for warning in warnings:
                print(f"  {warning}")
            return False
        else:
            print("✅ No duplicate title warnings found!")
            
            # Verify Beautiful Dangerous handling
            beautiful_dangerous_hacks = [h for h in all_hacks if h['title'] == 'Beautiful Dangerous']
            current_beautiful_dangerous = [h for h in current_hacks if h['title'] == 'Beautiful Dangerous']
            
            print(f"📊 Beautiful Dangerous versions found:")
            print(f"  - Total versions (include_obsolete=True): {len(beautiful_dangerous_hacks)}")
            print(f"  - Current versions (include_obsolete=False): {len(current_beautiful_dangerous)}")
            
            for hack in beautiful_dangerous_hacks:
                obsolete_status = hack.get('obsolete', False)
                print(f"  - ID {hack['id']}: obsolete={obsolete_status}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_dashboard_no_warnings()
    if success:
        print("\n✅ Dashboard warning test PASSED!")
    else:
        print("\n❌ Dashboard warning test FAILED!")
