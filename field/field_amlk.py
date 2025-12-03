"""
Field AMLK Integration Module
Dynamic integration with ADAM kernel through letsgo.py

Field operates within ADAM kernel, using letsgo.py as the system interface.
This bridge provides dynamic kernel access for Field's adaptive operations.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
import threading
import queue
import subprocess

# Path to letsgo.py in repository root
LETSGO_PATH = Path(__file__).parent.parent / "letsgo.py"

class FieldAMLKBridge:
    """
    Bridge between Field and ADAM kernel (letsgo.py)
    
    Field operates within ADAM, using letsgo.py as the system interface.
    Provides dynamic kernel parameter access for Field's adaptive operations.
    """
    
    def __init__(self):
        self.letsgo_process = None
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_running = False
        self.log_file = "amlk_system.log"
        self.lock = threading.Lock()
        
    def start_amlk_os(self):
        """Start ADAM kernel interface (letsgo.py)"""
        if self.is_running:
            return True
            
        try:
            # Start letsgo.py as system process
            if not LETSGO_PATH.exists():
                self._log_error(f"letsgo.py not found at {LETSGO_PATH}")
                return False
                
            self.letsgo_process = subprocess.Popen(
                [sys.executable, str(LETSGO_PATH), "--no-color"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=str(LETSGO_PATH.parent)
            )
            self.is_running = True
            
            # Start output monitoring in separate thread
            self._start_output_monitor()
            
            self._log_info("ADAM kernel interface started successfully")
            return True
        except Exception as e:
            self._log_error(f"ADAM kernel startup failed: {e}")
            return False
    
    def _start_output_monitor(self):
        """Monitor letsgo.py output in separate thread"""
        def monitor():
            while self.is_running and self.letsgo_process:
                try:
                    line = self.letsgo_process.stdout.readline()
                    if line:
                        self.response_queue.put(line.strip())
                except:
                    break
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def execute_system_command(self, command: str) -> Optional[str]:
        """
        Execute system command through ADAM kernel (letsgo.py)
        Field uses this for system operations
        """
        if not self.is_running or not self.letsgo_process:
            return None
            
        try:
            with self.lock:
                # Send command to letsgo.py
                if not self.letsgo_process.stdin:
                    return None
                self.letsgo_process.stdin.write(f"{command}\n")
                self.letsgo_process.stdin.flush()
                
                # Wait for response (with timeout)
                try:
                    response = self.response_queue.get(timeout=5.0)
                    return response
                except queue.Empty:
                    return None
        except Exception as e:
            self._log_error(f"Command execution error: {e}")
            return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information through ADAM kernel"""
        info = {}
        
        # Basic system info through commands
        commands = {
            'pwd': 'pwd',
            'ls': 'ls -la',
            'memory': 'free -h' if os.name != 'nt' else 'dir',
            'processes': 'ps aux' if os.name != 'nt' else 'tasklist'
        }
        
        for key, cmd in commands.items():
            result = self.execute_system_command(cmd)
            if result:
                info[key] = result
                
        return info
    
    def field_system_call(self, operation: str, **kwargs) -> Any:
        """
        System calls for Field through ADAM kernel
        Main interface for Field to use OS operations
        """
        if operation == "file_ops":
            # Файловые операции
            action = kwargs.get('action')
            path = kwargs.get('path')
            
            if action == 'read':
                return self.execute_system_command(f"cat {path}")
            elif action == 'write':
                content = kwargs.get('content', '')
                # Используем echo для записи (безопасно для простого контента)
                return self.execute_system_command(f'echo "{content}" > {path}')
            elif action == 'list':
                return self.execute_system_command(f"ls -la {path}")
                
        elif operation == "process_ops":
            # Процессы и память
            action = kwargs.get('action')
            
            if action == 'list':
                return self.execute_system_command("ps aux")
            elif action == 'memory':
                return self.execute_system_command("free -h")
                
        elif operation == "network_ops":
            # Сетевые операции
            action = kwargs.get('action')
            
            if action == 'status':
                return self.execute_system_command("netstat -an")
                
        return None
    
    def shutdown_amlk(self):
        """Shutdown ADAM kernel interface gracefully"""
        if self.letsgo_process:
            try:
                if self.letsgo_process.stdin:
                    self.letsgo_process.stdin.write("exit\n")
                    self.letsgo_process.stdin.flush()
                self.letsgo_process.wait(timeout=5)
            except:
                self.letsgo_process.terminate()
            finally:
                self.is_running = False
                self.letsgo_process = None
    
    def _log_info(self, message: str):
        """Log info for system, not user"""
        try:
            with open(self.log_file, "a") as f:
                f.write(f"[ADAM:INFO] {message}\n")
        except:
            pass  # Fail silently if logging fails
    
    def _log_error(self, message: str):
        """Log errors for system"""
        try:
            with open(self.log_file, "a") as f:
                f.write(f"[ADAM:ERROR] {message}\n")
        except:
            pass  # Fail silently if logging fails

# Глобальный экземпляр моста
_amlk_bridge = None

def get_amlk_bridge() -> FieldAMLKBridge:
    """Get global instance of ADAM kernel bridge"""
    global _amlk_bridge
    if _amlk_bridge is None:
        _amlk_bridge = FieldAMLKBridge()
    return _amlk_bridge

def start_field_in_amlk():
    """
    Start Field within ADAM kernel
    Main integration function
    """
    bridge = get_amlk_bridge()
    
    if bridge.start_amlk_os():
        # Get system info for internal use
        sys_info = bridge.get_system_info()
        bridge._log_info(f"ADAM kernel active, sys_params: {len(sys_info)}")
        
        return bridge
    else:
        return None

if __name__ == "__main__":
    # Test integration
    bridge = start_field_in_amlk()
    
    if bridge:
        # Test system calls
        print("\n🔧 Testing system operations:")
        
        # Test file operations
        result = bridge.field_system_call("file_ops", action="list", path=".")
        print(f"File list: {result}")
        
        # Test processes
        result = bridge.field_system_call("process_ops", action="memory")
        print(f"System memory: {result}")
        
        # Shutdown
        bridge.shutdown_amlk()
        print("🏁 ADAM kernel shutdown complete")
