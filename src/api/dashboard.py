"""Next.js dashboard serving endpoint"""

import os
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import FastAPI, Request
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

def setup_dashboard(app: FastAPI):
    """Mount Next.js dashboard to FastAPI"""
    
    # Dashboard root path
    dashboard_path = Path(__file__).parent.parent / "dashboard"
    public_path = dashboard_path / "public"
    next_path = dashboard_path / ".next"
    
    # Try to mount public directory if it exists
    if public_path.exists():
        app.mount("/public", StaticFiles(directory=public_path, html=False), name="public")
    
    # Root path serves dashboard
    @app.get("/", response_class=FileResponse)
    async def serve_dashboard():
        """Serve dashboard index.html"""
        dashboard_html = dashboard_path / "public" / "index.html"
        
        # If Next.js build exists, use that
        # Otherwise fall back to simple HTML
        if not dashboard_html.exists():
            # Create a simple redirect to Next.js running on 3000
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Akash Autopilot Dashboard</title>
                <script>
                    // Redirect to Next.js server if available
                    if (window.location.port !== '3000') {
                        // Try localhost:3000 first
                        fetch('http://localhost:3000').then(() => {
                            window.location.href = 'http://localhost:3000';
                        }).catch(() => {
                            // Fallback message
                            document.body.innerHTML = 'Dashboard loading... <br> Make sure Next.js dev server is running on port 3000';
                        });
                    }
                </script>
            </head>
            <body>Loading...</body>
            </html>
            """)
        
        return FileResponse(dashboard_html)
