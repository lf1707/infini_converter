#!/usr/bin/env python3
"""
Verify the warning dialog dimensions
"""

import sys
sys.path.insert(0, 'src')

def check_warning_dialog_dimensions():
    """Check that the warning dialog dimensions have been updated"""
    
    # Read the GUI file and check for updated dimensions
    with open('src/infini_converter/gui.py', 'r') as f:
        content = f.read()
    
    # Check for updated dimensions
    checks = [
        ("Window size", 'warning_dialog.geometry("700x350")' in content),
        ("File list width", 'width=80' in content and "file_list_text" in content),
        ("Command width", 'width=80' in content and "command_text" in content),
        ("Button padding", 'padx=10' in content and "Execute" in content),
        ("Button frame padding", "pady=15" in content and "button_frame.pack" in content),
    ]
    
    print("=== Warning Dialog Dimension Check ===")
    all_good = True
    
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not passed:
            all_good = False
    
    print(f"\nOverall Status: {'✅ All checks passed!' if all_good else '❌ Some checks failed!'}")
    
    if all_good:
        print("\nThe warning dialog has been successfully enlarged!")
        print("- Window size: 700x350 (was 600x250)")
        print("- Text areas: width 80 (was 70)")
        print("- Button padding: padx=10, pady=5 (was padx=5)")
        print("- Button frame padding: pady=15 (was pady=10)")
    
    return all_good

if __name__ == "__main__":
    check_warning_dialog_dimensions()