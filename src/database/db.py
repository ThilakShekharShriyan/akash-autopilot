"""SQLite database for persistent storage"""

import aiosqlite
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AutopilotDB:
    """Async SQLite database for Akash Autopilot"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
        
    async def connect(self):
        """Connect to database and initialize schema"""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        await self._init_schema()
        logger.info(f"Database connected: {self.db_path}")
        
    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            logger.info("Database connection closed")
    
    async def _init_schema(self):
        """Initialize database tables"""
        await self.conn.executescript("""
            -- Policy configuration
            CREATE TABLE IF NOT EXISTS policy (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            
            -- Deployment state tracking
            CREATE TABLE IF NOT EXISTS deployment_state (
                deployment_id TEXT PRIMARY KEY,
                name TEXT,
                status TEXT,
                replicas INTEGER,
                last_checked TEXT NOT NULL,
                metrics TEXT,
                updated_at TEXT NOT NULL
            );
            
            -- Action audit ledger
            CREATE TABLE IF NOT EXISTS action_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                deployment_id TEXT,
                details TEXT,
                status TEXT NOT NULL,
                error TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            
            -- Cooldown tracking
            CREATE TABLE IF NOT EXISTS cooldowns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                deployment_id TEXT,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            
            -- Indexes for performance
            CREATE INDEX IF NOT EXISTS idx_action_ledger_timestamp 
                ON action_ledger(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_action_ledger_type 
                ON action_ledger(action_type);
            CREATE INDEX IF NOT EXISTS idx_cooldowns_expires 
                ON cooldowns(expires_at);
            CREATE INDEX IF NOT EXISTS idx_cooldowns_action 
                ON cooldowns(action_type, deployment_id);
        """)
        await self.conn.commit()
        logger.info("Database schema initialized")
    
    # ===== ACTION LEDGER =====
    
    async def log_action(
        self,
        action_type: str,
        deployment_id: Optional[str] = None,
        details: Optional[Dict] = None,
        status: str = "pending",
        error: Optional[str] = None
    ) -> int:
        """Log an action to the audit ledger"""
        timestamp = datetime.utcnow().isoformat()
        cursor = await self.conn.execute("""
            INSERT INTO action_ledger 
            (timestamp, action_type, deployment_id, details, status, error)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            action_type,
            deployment_id,
            json.dumps(details) if details else None,
            status,
            error
        ))
        await self.conn.commit()
        logger.info(f"Action logged: {action_type} [{status}]")
        return cursor.lastrowid
    
    async def update_action_status(
        self,
        action_id: int,
        status: str,
        error: Optional[str] = None
    ):
        """Update action status"""
        await self.conn.execute("""
            UPDATE action_ledger
            SET status = ?, error = ?
            WHERE id = ?
        """, (status, error, action_id))
        await self.conn.commit()
    
    async def get_recent_actions(self, limit: int = 50) -> List[Dict]:
        """Get recent actions from ledger"""
        cursor = await self.conn.execute("""
            SELECT * FROM action_ledger
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_actions_by_type(
        self,
        action_type: str,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """Get actions of a specific type"""
        if since:
            cursor = await self.conn.execute("""
                SELECT * FROM action_ledger
                WHERE action_type = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (action_type, since.isoformat()))
        else:
            cursor = await self.conn.execute("""
                SELECT * FROM action_ledger
                WHERE action_type = ?
                ORDER BY timestamp DESC
            """, (action_type,))
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def count_actions_since(
        self,
        since: datetime,
        action_type: Optional[str] = None
    ) -> int:
        """Count actions since a timestamp"""
        if action_type:
            cursor = await self.conn.execute("""
                SELECT COUNT(*) FROM action_ledger
                WHERE timestamp >= ? AND action_type = ?
            """, (since.isoformat(), action_type))
        else:
            cursor = await self.conn.execute("""
                SELECT COUNT(*) FROM action_ledger
                WHERE timestamp >= ?
            """, (since.isoformat(),))
        
        row = await cursor.fetchone()
        return row[0]
    
    # ===== COOLDOWN MANAGEMENT =====
    
    async def set_cooldown(
        self,
        action_type: str,
        cooldown_seconds: int,
        deployment_id: Optional[str] = None
    ):
        """Set a cooldown period for an action"""
        expires_at = datetime.utcnow() + timedelta(seconds=cooldown_seconds)
        await self.conn.execute("""
            INSERT INTO cooldowns (action_type, deployment_id, expires_at)
            VALUES (?, ?, ?)
        """, (action_type, deployment_id, expires_at.isoformat()))
        await self.conn.commit()
        logger.debug(f"Cooldown set: {action_type} until {expires_at}")
    
    async def check_cooldown(
        self,
        action_type: str,
        deployment_id: Optional[str] = None
    ) -> bool:
        """Check if action is in cooldown period (True = in cooldown)"""
        now = datetime.utcnow().isoformat()
        
        if deployment_id:
            cursor = await self.conn.execute("""
                SELECT COUNT(*) FROM cooldowns
                WHERE action_type = ? 
                  AND deployment_id = ?
                  AND expires_at > ?
            """, (action_type, deployment_id, now))
        else:
            cursor = await self.conn.execute("""
                SELECT COUNT(*) FROM cooldowns
                WHERE action_type = ?
                  AND expires_at > ?
            """, (action_type, now))
        
        row = await cursor.fetchone()
        return row[0] > 0
    
    async def cleanup_expired_cooldowns(self):
        """Remove expired cooldowns"""
        now = datetime.utcnow().isoformat()
        await self.conn.execute("""
            DELETE FROM cooldowns
            WHERE expires_at <= ?
        """, (now,))
        await self.conn.commit()
    
    # ===== DEPLOYMENT STATE =====
    
    async def update_deployment_state(
        self,
        deployment_id: str,
        name: str,
        status: str,
        replicas: int,
        metrics: Optional[Dict] = None
    ):
        """Update deployment state"""
        now = datetime.utcnow().isoformat()
        await self.conn.execute("""
            INSERT INTO deployment_state 
            (deployment_id, name, status, replicas, last_checked, metrics, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(deployment_id) DO UPDATE SET
                name = excluded.name,
                status = excluded.status,
                replicas = excluded.replicas,
                last_checked = excluded.last_checked,
                metrics = excluded.metrics,
                updated_at = excluded.updated_at
        """, (
            deployment_id,
            name,
            status,
            replicas,
            now,
            json.dumps(metrics) if metrics else None,
            now
        ))
        await self.conn.commit()
    
    async def get_deployment_state(self, deployment_id: str) -> Optional[Dict]:
        """Get deployment state"""
        cursor = await self.conn.execute("""
            SELECT * FROM deployment_state
            WHERE deployment_id = ?
        """, (deployment_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def get_all_deployments(self) -> List[Dict]:
        """Get all tracked deployments"""
        cursor = await self.conn.execute("""
            SELECT * FROM deployment_state
            ORDER BY updated_at DESC
        """)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ===== POLICY MANAGEMENT =====
    
    async def set_policy(self, key: str, value: str):
        """Set or update a policy value"""
        now = datetime.utcnow().isoformat()
        await self.conn.execute("""
            INSERT INTO policy (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """, (key, value, now))
        await self.conn.commit()
    
    async def get_policy(self, key: str) -> Optional[str]:
        """Get a policy value"""
        cursor = await self.conn.execute("""
            SELECT value FROM policy
            WHERE key = ?
        """, (key,))
        row = await cursor.fetchone()
        return row[0] if row else None
    
    async def get_all_policies(self) -> Dict[str, str]:
        """Get all policy values"""
        cursor = await self.conn.execute("SELECT key, value FROM policy")
        rows = await cursor.fetchall()
        return {row[0]: row[1] for row in rows}
    
    # ===== STATISTICS =====
    
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        # Total actions
        cursor = await self.conn.execute("SELECT COUNT(*) FROM action_ledger")
        row = await cursor.fetchone()
        stats["total_actions"] = row[0]
        
        # Actions by status
        cursor = await self.conn.execute("""
            SELECT status, COUNT(*) as count
            FROM action_ledger
            GROUP BY status
        """)
        rows = await cursor.fetchall()
        stats["actions_by_status"] = {row[0]: row[1] for row in rows}
        
        # Recent actions (last hour)
        one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        cursor = await self.conn.execute("""
            SELECT COUNT(*) FROM action_ledger
            WHERE timestamp >= ?
        """, (one_hour_ago,))
        row = await cursor.fetchone()
        stats["actions_last_hour"] = row[0]
        
        # Tracked deployments
        cursor = await self.conn.execute("SELECT COUNT(*) FROM deployment_state")
        row = await cursor.fetchone()
        stats["tracked_deployments"] = row[0]
        
        # Active cooldowns
        now = datetime.utcnow().isoformat()
        cursor = await self.conn.execute("""
            SELECT COUNT(*) FROM cooldowns
            WHERE expires_at > ?
        """, (now,))
        row = await cursor.fetchone()
        stats["active_cooldowns"] = row[0]
        
        return stats
