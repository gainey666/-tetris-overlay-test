"""
Web-based dashboard for Tetris Overlay statistics and real-time monitoring.
Provides a browser-based interface for viewing overlay data and statistics.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from stats.service import stats_service
from ui.current_settings import get

logger = logging.getLogger(__name__)

class WebDashboard:
    """Web-based dashboard for real-time monitoring and statistics."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Tetris Overlay Dashboard")
        self.connected_clients: List[WebSocket] = []
        self.running = False
        
        self._setup_middleware()
        self._setup_routes()
        
    def _setup_middleware(self):
        """Setup FastAPI middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def get_dashboard():
            """Serve the main dashboard HTML."""
            return self._get_dashboard_html()
            
        @self.app.get("/api/stats")
        async def get_stats():
            """Get current statistics."""
            try:
                global_stats = stats_service.get_global_stats()
                matches = stats_service.get_all_matches()
                
                return {
                    "global_stats": global_stats,
                    "recent_matches": [asdict(match) for match in matches[:10]],
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                return {"error": str(e)}
                
        @self.app.get("/api/settings")
        async def get_settings():
            """Get current settings."""
            try:
                settings = get()
                return {
                    "roi_left": settings.roi_left,
                    "roi_right": settings.roi_right,
                    "prediction_agent": settings.prediction_agent,
                    "ghost": {
                        "colour": settings.ghost.colour,
                        "opacity": settings.ghost.opacity
                    },
                    "hotkeys": {
                        "toggle_overlay": settings.hotkeys.toggle_overlay,
                        "open_settings": settings.hotkeys.open_settings,
                        "open_stats": settings.hotkeys.open_stats
                    }
                }
            except Exception as e:
                logger.error(f"Error getting settings: {e}")
                return {"error": str(e)}
                
        @self.app.get("/api/matches")
        async def get_matches(limit: int = 50):
            """Get match history."""
            try:
                matches = stats_service.get_all_matches()
                return {
                    "matches": [asdict(match) for match in matches[:limit]],
                    "total": len(matches)
                }
            except Exception as e:
                logger.error(f"Error getting matches: {e}")
                return {"error": str(e)}
                
        @self.app.get("/api/match/{match_id}")
        async def get_match_detail(match_id: int):
            """Get detailed match information."""
            try:
                match_stats = stats_service.get_match_stats(match_id)
                if match_stats:
                    return asdict(match_stats)
                else:
                    return {"error": "Match not found"}
            except Exception as e:
                logger.error(f"Error getting match detail: {e}")
                return {"error": str(e)}
                
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.connected_clients.append(websocket)
            
            try:
                while True:
                    # Send periodic updates
                    await self._send_real_time_update(websocket)
                    await asyncio.sleep(1)  # Update every second
                    
            except WebSocketDisconnect:
                self.connected_clients.remove(websocket)
                logger.info("WebSocket client disconnected")
                
    async def _send_real_time_update(self, websocket: WebSocket):
        """Send real-time update to WebSocket client."""
        try:
            # Get current overlay state
            settings = get()
            global_stats = stats_service.get_global_stats()
            
            update_data = {
                "type": "real_time_update",
                "timestamp": datetime.now().isoformat(),
                "settings": {
                    "ghost_colour": settings.ghost.colour,
                    "ghost_opacity": settings.ghost.opacity,
                    "show_combo": getattr(settings, 'show_combo', False),
                    "show_b2b": getattr(settings, 'show_b2b', False),
                    "show_fps": getattr(settings, 'show_fps', False)
                },
                "stats": global_stats,
                "performance": {
                    "fps": 30.0,  # Would get from performance monitor
                    "memory_usage": 100.0,  # Would get from system monitor
                    "cpu_usage": 5.0
                }
            }
            
            await websocket.send_text(json.dumps(update_data))
            
        except Exception as e:
            logger.error(f"Error sending real-time update: {e}")
            
    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tetris Overlay Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .dashboard {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #444;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }
        .stat-label {
            color: #888;
            margin-top: 5px;
        }
        .chart-container {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #444;
            margin-bottom: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-online { background-color: #4CAF50; }
        .status-offline { background-color: #f44336; }
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        .btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 0 10px;
        }
        .btn:hover { background: #45a049; }
        .btn:disabled { background: #666; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🎮 Tetris Overlay Dashboard</h1>
            <p>
                <span class="status-indicator status-online" id="status"></span>
                <span id="status-text">Connected</span>
            </p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-matches">0</div>
                <div class="stat-label">Total Matches</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-frames">0</div>
                <div class="stat-label">Total Frames</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-fps">30</div>
                <div class="stat-label">Average FPS</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="most-common">T</div>
                <div class="stat-label">Most Common Piece</div>
            </div>
        </div>

        <div class="chart-container">
            <h3>Performance Over Time</h3>
            <canvas id="performance-chart"></canvas>
        </div>

        <div class="chart-container">
            <h3>Piece Distribution</h3>
            <canvas id="piece-chart"></canvas>
        </div>

        <div class="controls">
            <button class="btn" onclick="refreshData()">Refresh Data</button>
            <button class="btn" onclick="exportData()">Export Stats</button>
            <button class="btn" id="toggle-overlay">Toggle Overlay</button>
        </div>
    </div>

    <script>
        let ws;
        let performanceChart;
        let pieceChart;

        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function() {
                updateStatus(true);
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'real_time_update') {
                    updateRealTimeData(data);
                }
            };
            
            ws.onclose = function() {
                updateStatus(false);
                // Try to reconnect after 3 seconds
                setTimeout(initWebSocket, 3000);
            };
            
            ws.onerror = function() {
                updateStatus(false);
            };
        }

        function updateStatus(connected) {
            const indicator = document.getElementById('status');
            const text = document.getElementById('status-text');
            
            if (connected) {
                indicator.className = 'status-indicator status-online';
                text.textContent = 'Connected';
            } else {
                indicator.className = 'status-indicator status-offline';
                text.textContent = 'Disconnected';
            }
        }

        function updateRealTimeData(data) {
            // Update stats
            document.getElementById('total-matches').textContent = data.stats.total_matches || 0;
            document.getElementById('total-frames').textContent = data.stats.total_frames || 0;
            document.getElementById('avg-fps').textContent = data.performance.fps.toFixed(1);
            document.getElementById('most-common').textContent = data.stats.most_common_piece || 'N/A';
            
            // Update performance chart
            if (performanceChart) {
                const now = new Date();
                performanceChart.data.labels.push(now.toLocaleTimeString());
                performanceChart.data.datasets[0].data.push(data.performance.fps);
                
                // Keep only last 20 data points
                if (performanceChart.data.labels.length > 20) {
                    performanceChart.data.labels.shift();
                    performanceChart.data.datasets[0].data.shift();
                }
                
                performanceChart.update('none');
            }
        }

        function initCharts() {
            // Performance chart
            const perfCtx = document.getElementById('performance-chart').getContext('2d');
            performanceChart = new Chart(perfCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'FPS',
                        data: [],
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 60
                        }
                    }
                }
            });

            // Piece distribution chart
            const pieceCtx = document.getElementById('piece-chart').getContext('2d');
            pieceChart = new Chart(pieceCtx, {
                type: 'doughnut',
                data: {
                    labels: ['I', 'O', 'T', 'S', 'Z', 'J', 'L'],
                    datasets: [{
                        data: [0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: [
                            '#00ffff', '#ffff00', '#ff00ff', 
                            '#00ff00', '#ff0000', '#0000ff', '#ff8000'
                        ]
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }

        async function refreshData() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                // Update piece distribution
                if (data.global_stats.piece_frequency) {
                    pieceChart.data.datasets[0].data = [
                        data.global_stats.piece_frequency.I || 0,
                        data.global_stats.piece_frequency.O || 0,
                        data.global_stats.piece_frequency.T || 0,
                        data.global_stats.piece_frequency.S || 0,
                        data.global_stats.piece_frequency.Z || 0,
                        data.global_stats.piece_frequency.J || 0,
                        data.global_stats.piece_frequency.L || 0
                    ];
                    pieceChart.update();
                }
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }

        async function exportData() {
            try {
                const response = await fetch('/api/matches?limit=1000');
                const data = await response.json();
                
                const blob = new Blob([JSON.stringify(data, null, 2)], 
                                     { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `tetris-stats-${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
            } catch (error) {
                console.error('Error exporting data:', error);
            }
        }

        // Initialize everything
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            initWebSocket();
            refreshData();
        });
    </script>
</body>
</html>
        """
        
    async def start_server(self):
        """Start the web dashboard server."""
        if not self.running:
            self.running = True
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            
            logger.info(f"Starting web dashboard on http://{self.host}:{self.port}")
            await server.serve()
            
    def stop_server(self):
        """Stop the web dashboard server."""
        self.running = False
        
    async def broadcast_update(self, data: Dict[str, Any]):
        """Broadcast update to all connected WebSocket clients."""
        if self.connected_clients:
            message = json.dumps(data)
            disconnected_clients = []
            
            for client in self.connected_clients:
                try:
                    await client.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    disconnected_clients.append(client)
                    
            # Remove disconnected clients
            for client in disconnected_clients:
                self.connected_clients.remove(client)

# Global dashboard instance
web_dashboard = WebDashboard()
