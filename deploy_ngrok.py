#!/usr/bin/env python3
"""
ngrok Deployment Script for Simple API Test Application

This script starts the FastAPI server and creates an ngrok tunnel for remote access.
Perfect for testing the API from external programs or sharing with others.

Usage:
    python deploy_ngrok.py [--port PORT] [--auth-token TOKEN]

Requirements:
    - ngrok installed (https://ngrok.com/download)
    - pyngrok package (pip install pyngrok)
"""

import argparse
import asyncio
import signal
import sys
import time
import threading
from pathlib import Path

try:
    from pyngrok import ngrok, conf
    from pyngrok.exception import PyngrokNgrokError
except ImportError:
    print("❌ pyngrok not found. Install with: pip install pyngrok")
    print("   Or install ngrok manually and use ngrok_deploy.sh instead")
    sys.exit(1)

import uvicorn
from main import app


class NgrokDeployment:
    def __init__(self, port=8000, auth_token=None):
        self.port = port
        self.auth_token = auth_token
        self.tunnel = None
        self.server_thread = None
        self.should_stop = False
        
    def setup_ngrok(self):
        """Configure ngrok settings"""
        if self.auth_token:
            ngrok.set_auth_token(self.auth_token)
            print(f"✅ Set ngrok auth token")
        
        # Kill any existing ngrok processes
        ngrok.kill()
        
    def start_server(self):
        """Start FastAPI server in a separate thread"""
        def run_server():
            try:
                uvicorn.run(
                    app, 
                    host="127.0.0.1", 
                    port=self.port,
                    log_level="info",
                    access_log=True
                )
            except Exception as e:
                if not self.should_stop:
                    print(f"❌ Server error: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Give server time to start
        print(f"🚀 Starting FastAPI server on port {self.port}...")
        time.sleep(3)
        
    def create_tunnel(self):
        """Create ngrok tunnel"""
        try:
            self.tunnel = ngrok.connect(self.port, "http")
            public_url = self.tunnel.public_url
            return public_url
        except PyngrokNgrokError as e:
            print(f"❌ ngrok error: {e}")
            return None
        except Exception as e:
            print(f"❌ Tunnel creation failed: {e}")
            return None
    
    def display_info(self, public_url):
        """Display deployment information"""
        print("\n" + "="*60)
        print("🌐 API DEPLOYED WITH NGROK")
        print("="*60)
        print(f"📍 Local URL:     http://localhost:{self.port}")
        print(f"🔗 Public URL:    {public_url}")
        print(f"📚 API Docs:      {public_url}/docs")
        print(f"📖 ReDoc:         {public_url}/redoc")
        print(f"💓 Health Check:  {public_url}/health")
        print("="*60)
        print("\n🔧 TESTING ENDPOINTS:")
        print(f"  Users:     {public_url}/users")
        print(f"  Items:     {public_url}/items")
        print(f"  Root:      {public_url}/")
        print("\n💡 Use these URLs in your external testing programs!")
        print("\n⚠️  Press Ctrl+C to stop the deployment")
        print("-"*60)
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🔄 Shutting down...")
        self.should_stop = True
        
        if self.tunnel:
            try:
                ngrok.disconnect(self.tunnel.public_url)
                print("✅ Closed ngrok tunnel")
            except:
                pass
        
        try:
            ngrok.kill()
            print("✅ Stopped ngrok process")
        except:
            pass
        
        print("👋 Deployment stopped")
    
    def deploy(self):
        """Main deployment function"""
        try:
            print("🔧 Setting up ngrok...")
            self.setup_ngrok()
            
            self.start_server()
            
            print("🌐 Creating ngrok tunnel...")
            public_url = self.create_tunnel()
            
            if not public_url:
                print("❌ Failed to create tunnel")
                return False
            
            self.display_info(public_url)
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False
        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Simple API Test Application with ngrok"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to run the API server (default: 8000)"
    )
    parser.add_argument(
        "--auth-token",
        type=str,
        help="ngrok auth token for advanced features"
    )
    
    args = parser.parse_args()
    
    deployment = NgrokDeployment(port=args.port, auth_token=args.auth_token)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        deployment.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    success = deployment.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()