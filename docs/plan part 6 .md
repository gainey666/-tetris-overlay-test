📋 Plan for Completing the Overlay (45 min coding sprint) - ✅ **COMPLETED**

🎯 **IMPLEMENTATION STATUS: FULLY COMPLETE**

✅ **All 9 Steps Implemented Successfully:**

1️⃣ **Add CURRENT singleton & import pygame** - ✅ DONE
   - Added `import pygame` for display.flip()
   - Created global `CURRENT_SETTINGS` singleton
   - Created global `overlay_renderer` instance

2️⃣ **Dynamic hot-key registration** - ✅ DONE
   - Implemented `_register_dynamic_hotkeys()` function
   - Reads from `CURRENT_SETTINGS.hotkeys`
   - Registers all hotkeys including settings and stats dashboard

3️⃣ **Extend OverlayRenderer** - ✅ DONE
   - Added `update_ghost_style(colour, opacity)` method
   - Updated `draw_ghost()` to use configurable style
   - Clean special move indicators (TSPIN, B2B, combo)

4️⃣ **Replace renderer creation** - ✅ DONE
   - Uses global `overlay_renderer` in `process_frames()`
   - No more duplicate renderer instances

5️⃣ **Implement frame-worker thread** - ✅ DONE
   - Added `_frame_worker()` with 30 FPS throttling
   - Daemon thread for continuous frame processing
   - Error handling prevents thread crashes

6️⃣ **Integrate stats.collector** - ✅ DONE
   - Stats recording in each `process_frames()` call
   - `start_new_match()` on application launch
   - `end_current_match()` on graceful exit

7️⃣ **Add dashboard hot-key** - ✅ DONE
   - `StatsDashboard().show()` registered to `open_stats` hotkey
   - Non-blocking Qt window launch

8️⃣ **Update graceful exit** - ✅ DONE
   - Calls `end_current_match()` before shutdown
   - Proper stats database cleanup

9️⃣ **Minor clean-up** - ✅ DONE
   - Added required imports (`threading`, `time`)
   - Fixed lint errors and duplicate code
   - All tests passing

🎮 **FINAL RESULT:**
- ✅ **30 FPS overlay loop** running continuously
- ✅ **Real ghost piece rendering** with configurable style
- ✅ **Live settings configuration** with instant updates
- ✅ **Statistics tracking** recording every frame
- ✅ **Dynamic hotkey system** from user settings
- ✅ **Professional error handling** with fallback modes

📢 **READY FOR "COOK WHILE IT RUNS" EXPERIENCE!**

The overlay now:
- Runs at 30 FPS in background thread
- Draws ghost pieces with user-configurable colors
- Records statistics to SQLite database
- Responds to all hotkeys (F9, F1, Ctrl+Alt+S, etc.)
- Maintains settings persistence
- Handles errors gracefully

**Implementation Time: ~45 minutes as planned ✅**