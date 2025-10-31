#!/usr/bin/env python3
"""
Toko Kredit Syariah - Android Launcher
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main app
try:
    from main import TokoKreditSyariahApp
    app = TokoKreditSyariahApp()
    app.run()
except Exception as e:
    print(f"Error starting app: {e}")
    import traceback
    traceback.print_exc()
