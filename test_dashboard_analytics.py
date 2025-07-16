#!/usr/bin/env python3
"""
Test script to verify that Dashboard analytics work correctly with selective obsolete filtering
"""

def test_dashboard_analytics():
    """Test that Dashboard analytics handle obsolete filtering correctly"""
    from hack_data_manager import HackDataManager
    from ui.dashboard.analytics import DashboardAnalytics
    import io
    import sys
    from contextlib import redirect_stdout
    
    print("🧪 Testing Dashboard analytics with selective obsolete filtering...")
    
    try:
        # Initialize components
        data_manager = HackDataManager()
        analytics = DashboardAnalytics(data_manager)
        
        # Capture output to check for warnings
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            # Load analytics data (this triggers the dual dataset creation)
            analytics.load_analytics_data()
            
            # Calculate analytics (these update analytics_data internally)
            analytics._calculate_basic_stats()
            analytics._calculate_completion_data()
        
        # Check captured output for warnings
        output = captured_output.getvalue()
        warnings = [line for line in output.split('\n') if 'WARNING: Duplicate title' in line]
        
        if warnings:
            print(f"❌ Found {len(warnings)} warnings in analytics:")
            for warning in warnings:
                print(f"  {warning}")
            return False
        else:
            print("✅ No duplicate title warnings found in analytics!")
            
        # Verify that analytics data is working
        print(f"📊 Analytics Results:")
        print(f"  - Total Hacks (current): {analytics.analytics_data.get('total_hacks', 'N/A')}")
        print(f"  - Completed Hacks: {analytics.analytics_data.get('completed_hacks', 'N/A')}")
        print(f"  - Completion Rate: {analytics.analytics_data.get('completion_rate', 'N/A')}%")
        
        # Verify Beautiful Dangerous is handled correctly
        beautiful_dangerous_current = [h for h_id, h in analytics.current_data.items() 
                                     if isinstance(h, dict) and h.get('title') == 'Beautiful Dangerous']
        beautiful_dangerous_all = [h for h_id, h in analytics.all_data.items() 
                                 if isinstance(h, dict) and h.get('title') == 'Beautiful Dangerous']
        
        print(f"  - Beautiful Dangerous in current_data: {len(beautiful_dangerous_current)}")
        print(f"  - Beautiful Dangerous in all_data: {len(beautiful_dangerous_all)}")
        
        return True
            
    except Exception as e:
        print(f"❌ Error during analytics test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard_analytics()
    if success:
        print("\n✅ Dashboard analytics test PASSED!")
    else:
        print("\n❌ Dashboard analytics test FAILED!")
