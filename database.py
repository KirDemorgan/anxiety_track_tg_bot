import asyncpg
import os
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.database_url)
    
    async def add_pill(self, user_id: int, pill_name: str, dose: str) -> bool:
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    'INSERT INTO pills (user_id, pill_name, dose) VALUES ($1, $2, $3)',
                    user_id, pill_name, dose
                )
            return True
        except Exception as e:
            print(f"Error adding pill: {e}")
            return False
    
    async def add_health_note(self, user_id: int, note: str) -> bool:
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    'INSERT INTO health_notes (user_id, note) VALUES ($1, $2)',
                    user_id, note
                )
            return True
        except Exception as e:
            print(f"Error adding health note: {e}")
            return False
    
    async def get_user_data(self, user_id: int) -> Dict:
        async with self.pool.acquire() as conn:
            pills = await conn.fetch(
                'SELECT pill_name, dose, taken_at FROM pills WHERE user_id = $1 ORDER BY taken_at',
                user_id
            )
            
            notes = await conn.fetch(
                'SELECT note, created_at FROM health_notes WHERE user_id = $1 ORDER BY created_at',
                user_id
            )
            
            return {
                'pills': [dict(row) for row in pills],
                'notes': [dict(row) for row in notes]
            }
    
    async def close(self):
        if self.pool:
            await self.pool.close()