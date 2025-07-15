#!/usr/bin/env python3
"""
Multi-type download utilities for handling hacks with multiple types
"""

import os
import shutil


def handle_multi_type_download(primary_output_path, hack_types, output_dir, folder_name, title_clean, base_rom_ext, config, log=None):
    """
    Handle multi-type downloads based on user settings
    
    Args:
        primary_output_path: Path to the primary (first) type location
        hack_types: List of hack types (e.g., ['kaizo', 'tool_assisted'])
        output_dir: Base output directory
        folder_name: Difficulty folder name
        title_clean: Clean hack title for filename
        base_rom_ext: ROM file extension
        config: ConfigManager instance
        log: Optional logging function
        
    Returns:
        List of additional paths created (empty if only primary)
    """
    from api_pipeline import make_output_path
    
    additional_paths = []
    
    # Get multi-type settings
    multi_type_enabled = config.get("multi_type_enabled", True)
    download_mode = config.get("multi_type_download_mode", "primary_only")
    
    # Only proceed if multi-type is enabled and hack has multiple types
    if not multi_type_enabled or len(hack_types) <= 1 or download_mode == "primary_only":
        return additional_paths
    
    if log:
        log(f"📁 Creating multi-type copies for {len(hack_types)} types: {', '.join(hack_types)}", "Information")
    
    # Create additional copies for other types
    output_filename = f"{title_clean}{base_rom_ext}"
    
    for hack_type in hack_types[1:]:  # Skip primary type (already created)
        additional_path = os.path.join(make_output_path(output_dir, hack_type, folder_name), output_filename)
        
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(additional_path), exist_ok=True)
            
            # Create a full copy to the additional type folder
            shutil.copy2(primary_output_path, additional_path)
            if log:
                log(f"� Copied to {hack_type.title()} folder", "Debug")
            
            additional_paths.append(additional_path)
            
        except Exception as e:
            if log:
                log(f"⚠️ Failed to create {hack_type} copy: {str(e)}", "Error")
            # Continue with other types even if one fails
    
    return additional_paths


def get_hack_types_from_raw_data(raw_fields, hack_data=None):
    """
    Extract hack types from raw fields or hack data
    
    Args:
        raw_fields: Raw fields from hack data
        hack_data: Optional full hack data (fallback)
        
    Returns:
        List of normalized hack types
    """
    # Try to get types from raw_fields first
    hack_types_raw = raw_fields.get("type") if raw_fields else None
    
    # Fallback to hack_data if available
    if not hack_types_raw and hack_data:
        hack_types_raw = hack_data.get("type", "")
    
    # Handle both list and string formats
    if isinstance(hack_types_raw, list):
        hack_types = [t.lower().replace("-", "_") for t in hack_types_raw if t]
    else:
        hack_types = [hack_types_raw.lower().replace("-", "_")] if hack_types_raw else ["standard"]
    
    # Ensure we have at least one type
    if not hack_types:
        hack_types = ["standard"]
    
    return hack_types
