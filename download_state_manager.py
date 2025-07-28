"""
Simple Download State Manager
Simple global flag to prevent collection editing during downloads
"""

# Simple global flags - no complex threading
_download_active = False
_callbacks = []

def is_download_active():
    """Check if a download is currently active"""
    return _download_active

def set_download_active(active):
    """Set download state and notify callbacks"""
    global _download_active
    old_state = _download_active
    _download_active = active
    
    # Only notify if state actually changed
    if old_state != active:
        for callback in _callbacks.copy():  # Copy to avoid modification during iteration
            try:
                callback(active)
            except Exception as e:
                print(f"Error in download state callback: {e}")

def register_callback(callback):
    """Register a callback for download state changes"""
    if callback not in _callbacks:
        _callbacks.append(callback)

def unregister_callback(callback):
    """Unregister a download state callback"""
    if callback in _callbacks:
        _callbacks.remove(callback)
