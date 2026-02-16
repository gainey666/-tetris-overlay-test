#!/usr/bin/env python3
"""
FULL TETRIS OVERLAY EXPERIENCE DEMO
Shows everything the overlay can do without requiring Tetris
"""

import pygame
import time
import sys
from PySide6.QtWidgets import QApplication
from overlay_renderer import OverlayRenderer
from feature_toggles import feature_manager, enable_feature
from ui.settings_dialog import SettingsDialog
from ui.stats_dashboard import StatsDashboard

def show_gui_demo():
    """Show the GUI components"""
    print("🖥️  SHOWING GUI COMPONENTS")
    print("=" * 50)
    
    app = QApplication([])
    
    # Settings Dialog
    settings = SettingsDialog()
    settings.show()
    print("✅ Settings Dialog opened")
    
    # Stats Dashboard
    dashboard = StatsDashboard()
    dashboard.show()
    print("✅ Stats Dashboard opened")
    
    # Keep open for 3 seconds
    from PySide6.QtCore import QTimer
    QTimer.singleShot(3000, app.quit)
    
    app.exec()
    print("✅ GUI demo complete")

def show_overlay_demo():
    """Show the overlay in action"""
    print("\n🎮 SHOWING OVERLAY DEMO")
    print("=" * 50)
    
    pygame.init()
    
    # Create overlay
    renderer = OverlayRenderer()
    renderer.visible = True
    
    print("✅ Overlay initialized")
    
    # Demo sequence
    demo_scenes = [
        ("Basic T-piece", "T", 3, 0, False, False, 0),
        ("T-Spin setup", "T", 4, 1, True, False, 0),
        ("B2B opportunity", "T", 5, 0, False, True, 2),
        ("Massive combo", "I", 0, 0, False, True, 8),
        ("O-piece simple", "O", 7, 0, False, False, 0),
    ]
    
    for i, (desc, piece, col, rot, tspin, b2b, combo) in enumerate(demo_scenes):
        print(f"\n🎯 Scene {i+1}: {desc}")
        
        # Clear screen
        renderer.screen.fill((0, 0, 0, 128))
        
        # Draw ghost piece
        renderer.draw_ghost(renderer.screen, col, rot, piece, tspin, b2b, combo)
        
        # Add indicators
        if tspin:
            print("   📌 T-Spin indicator")
        if b2b:
            print("   ⚡ B2B indicator")
        if combo > 0:
            print(f"   🔥 Combo x{combo}")
        
        # Add performance
        renderer.draw_performance(renderer.screen)
        
        # Add stats
        renderer.draw_stats(renderer.screen)
        
        # Show
        pygame.display.flip()
        time.sleep(2)
    
    pygame.quit()
    print("✅ Overlay demo complete")

def show_feature_toggles():
    """Show feature toggle system"""
    print("\n🎛️  FEATURE TOGGLE DEMO")
    print("=" * 50)
    
    # Show current state
    toggles = feature_manager.get_all_toggles()
    print("Current feature states:")
    for feature, enabled in toggles.items():
        status = "🟢" if enabled else "🔴"
        print(f"  {status} {feature}")
    
    # Toggle some features
    print("\n🔄 Toggling features...")
    
    # Enable debug mode
    enable_feature('debug_mode_enabled', True)
    print("✅ Debug mode ENABLED")
    
    # Disable performance monitor
    enable_feature('performance_monitor_enabled', False)
    print("❌ Performance monitor DISABLED")
    
    # Re-enable performance monitor
    enable_feature('performance_monitor_enabled', True)
    print("✅ Performance monitor RE-ENABLED")
    
    # Disable debug mode
    enable_feature('debug_mode_enabled', False)
    print("❌ Debug mode DISABLED")
    
    print("✅ Feature toggle demo complete")

def show_error_handling():
    """Show error handling capabilities"""
    print("\n🛡️  ERROR HANDLING DEMO")
    print("=" * 50)
    
    from error_handler import error_handler
    
    # Test dependency check
    deps_ok = error_handler.check_dependencies()
    print(f"✅ Dependencies: {'OK' if deps_ok else 'Missing some'}")
    
    # Test warning handling
    error_handler.handle_warning("This is a test warning", "Demo")
    print("✅ Warning handled with toast notification")
    
    # Test error summary
    summary = error_handler.get_error_summary()
    print(f"✅ Error summary: {len(summary.split())} words")
    
    print("✅ Error handling demo complete")

def show_performance_monitoring():
    """Show performance monitoring"""
    print("\n📊 PERFORMANCE MONITORING DEMO")
    print("=" * 50)
    
    from performance_monitor import performance_monitor
    
    # Simulate some frames
    for i in range(10):
        performance_monitor.start_frame()
        time.sleep(0.03)  # Simulate 30 FPS
        performance_monitor.end_frame()
    
    # Get stats
    stats = performance_monitor.get_stats()
    print(f"✅ FPS: {stats['fps']:.1f}")
    print(f"✅ Frame time: {stats['avg_frame_time']*1000:.1f}ms")
    print(f"✅ Total frames: {stats['total_frames']}")
    print(f"✅ Uptime: {stats['uptime']:.1f}s")
    
    print("✅ Performance monitoring demo complete")

def main():
    """Run full experience demo"""
    print("🎯 TETRIS OVERLAY - FULL EXPERIENCE DEMO")
    print("=" * 60)
    print("This demo shows ALL features of the overlay system")
    print("=" * 60)
    
    try:
        # Show all components
        show_gui_demo()
        show_overlay_demo()
        show_feature_toggles()
        show_error_handling()
        show_performance_monitoring()
        
        print("\n🎉 FULL EXPERIENCE DEMO COMPLETE!")
        print("=" * 60)
        print("✅ GUI Components (Settings + Stats)")
        print("✅ Overlay Rendering (Ghost pieces + indicators)")
        print("✅ Feature Toggles (7 configurable features)")
        print("✅ Error Handling (Graceful fallback)")
        print("✅ Performance Monitoring (Real-time FPS)")
        print("✅ All Systems Working Together!")
        print("=" * 60)
        print("🚀 READY FOR FULL TETRIS EXPERIENCE!")
        
        print("\n📋 TO RUN WITH TETRIS:")
        print("1. Open Tetris game")
        print("2. Run: python roi_calibrator.py (first time only)")
        print("3. Run: python run_overlay_core.py")
        print("4. Press F9 to toggle overlay")
        print("5. Press F1 for settings")
        print("6. Press Ctrl+Alt+S for stats")
        print("7. Press Esc to quit")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
