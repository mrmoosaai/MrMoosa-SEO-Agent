#!/usr/bin/env python3
"""Verify PDF Quick Fixes section formatting"""

try:
    from PyPDF2 import PdfReader
    
    with open('seo_audit_report.pdf', 'rb') as f:
        reader = PdfReader(f)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        
        # Find and display Quick Fixes section
        if 'QUICK FIXES' in text:
            idx = text.find('QUICK FIXES')
            section = text[idx:idx+2000]
            print('✅ QUICK FIXES SECTION FOUND:')
            print('=' * 80)
            print(section)
            print('=' * 80)
            
            # Check for escape sequences
            escape_chars = ['&lt;', '&gt;', '&quot;', '&amp;', '&#39;']
            found_escapes = [esc for esc in escape_chars if esc in section]
            
            if found_escapes:
                print(f'\n❌ ERROR: Found HTML escape sequences: {found_escapes}')
            else:
                print('\n✅ NO escape sequences detected - Code displays cleanly!')
            
            # Check for properly formed HTML tags
            if '<meta' in section or '<script' in section or '< ' in section:
                print('✅ HTML tags are properly formatted with angle brackets!')
            else:
                print('⚠️  No HTML tags found in extracted text (might be image/embedded)')
            
            # Check for word breaks
            if 'p' in section and ' ' not in section.split('p')[0].split('\n')[-1]:
                print('⚠️  Possible word breaking detected')
            else:
                print('✅ No obvious word breaking detected!')
        else:
            print('⚠️  QUICK FIXES section not found in PDF')
            print('Available sections:')
            for section in ['TECHNICAL', 'RECOMMENDATIONS', 'KEY METRICS']:
                if section in text:
                    print(f'  ✓ {section}')
                    
except ImportError:
    print('⚠️  PyPDF2 not installed')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
