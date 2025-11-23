"""
Database module for CinemaGuard
Handles Supabase connection and table operations
"""
import os
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import supabase with mandatory requirement
try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError(
        "Supabase package is required but not installed. "
        "Install it with: pip install supabase"
    )

# Get Supabase credentials - these are now REQUIRED
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Supabase credentials are required but not found in environment variables.\n"
        "Please set SUPABASE_URL and SUPABASE_KEY in your .env file.\n"
        "CinemaGuard cannot run without a database connection."
    )

# Create Supabase client - will raise exception if connection fails
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Supabase connected successfully")
except Exception as e:
    raise RuntimeError(
        f"Failed to connect to Supabase: {e}\n"
        "Please check your SUPABASE_URL and SUPABASE_KEY in .env file."
    )


async def init_tables():
    """Initialize database tables if they don't exist"""
    try:
        # Verify tables exist by attempting a basic query
        # Note: Supabase Python client doesn't have direct schema creation
        # Tables should be created via Supabase dashboard with this schema:
        
        # halls table:
        # - id: uuid (primary key, auto-generated)
        # - name: text (unique)
        # - grid_config: jsonb
        # - created_at: timestamp with time zone (default: now())
        
        # alerts table:
        # - id: uuid (primary key, auto-generated)
        # - hall_id: uuid (foreign key to halls.id)
        # - risk_score: float8
        # - zone: text
        # - timestamp: timestamp with time zone (default: now())
        
        # Test connection by querying halls table
        supabase.table("halls").select("id").limit(1).execute()
        print("✓ Database tables verified")
    except Exception as e:
        raise RuntimeError(
            f"Database table verification failed: {e}\n"
            "Please ensure 'halls' and 'alerts' tables exist in your Supabase project.\n"
            "See schema documentation in db.py for table structure."
        )


async def save_grid_config(hall_name: str, grid_config: Dict) -> Dict:
    """Save or update grid configuration for a hall"""
    try:
        # Check if hall exists
        result = supabase.table("halls").select("*").eq("name", hall_name).execute()
        
        if result.data:
            # Update existing hall
            response = supabase.table("halls").update({
                "grid_config": grid_config
            }).eq("name", hall_name).execute()
        else:
            # Insert new hall
            response = supabase.table("halls").insert({
                "name": hall_name,
                "grid_config": grid_config
            }).execute()
        
        if not response.data:
            raise RuntimeError(f"No data returned when saving grid config for hall: {hall_name}")
        
        print(f"✓ Grid config saved for hall: {hall_name}")
        return response.data[0]
    except Exception as e:
        error_msg = f"Failed to save grid config for hall '{hall_name}': {e}"
        print(f"✗ {error_msg}")
        raise RuntimeError(error_msg)


async def get_grid_config(hall_name: str) -> Optional[Dict]:
    """Retrieve grid configuration for a hall"""
    try:
        result = supabase.table("halls").select("grid_config").eq("name", hall_name).execute()
        if result.data:
            return result.data[0].get("grid_config")
        return None
    except Exception as e:
        error_msg = f"Failed to get grid config for hall '{hall_name}': {e}"
        print(f"✗ {error_msg}")
        raise RuntimeError(error_msg)


async def save_alert(hall_name: str, risk_score: float, zone: str) -> Dict:
    """Save a new alert to the database"""
    import time
    
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            # Get or create hall
            hall_result = supabase.table("halls").select("id").eq("name", hall_name).execute()
            
            if not hall_result.data:
                # Create hall if it doesn't exist
                print(f"Creating new hall: {hall_name}")
                new_hall = supabase.table("halls").insert({
                    "name": hall_name,
                    "grid_config": {}
                }).execute()
                
                if not new_hall.data:
                    raise RuntimeError(f"Failed to create hall: {hall_name}")
                
                hall_id = new_hall.data[0]["id"]
                print(f"✓ Hall created with ID: {hall_id}")
            else:
                hall_id = hall_result.data[0]["id"]
            
            # Insert alert with timestamp
            alert_data = {
                "hall_id": hall_id,
                "risk_score": risk_score,
                "zone": zone
            }
            
            response = supabase.table("alerts").insert(alert_data).execute()
            
            if not response.data:
                raise RuntimeError(f"No data returned when saving alert for zone: {zone}")
            
            alert_id = response.data[0].get("id", "unknown")
            timestamp = response.data[0].get("timestamp", "unknown")
            print(f"✓ Alert saved successfully - ID: {alert_id}, Zone: {zone}, Risk: {risk_score:.2f}, Timestamp: {timestamp}")
            return response.data[0]
            
        except Exception as e:
            error_msg = f"Failed to save alert (attempt {attempt + 1}/{max_retries}): {e}"
            print(f"✗ {error_msg}")
            
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                # Final attempt failed - log error but don't crash detection loop
                print(f"✗ CRITICAL: Failed to save alert after {max_retries} attempts. Alert data: zone={zone}, risk={risk_score}")
                return {}


async def get_recent_alerts(hall_name: str, limit: int = 10) -> List[Dict]:
    """Get recent alerts for a hall"""
    try:
        # Get hall ID
        hall_result = supabase.table("halls").select("id").eq("name", hall_name).execute()
        
        if not hall_result.data:
            # No hall found, return empty list
            return []
        
        hall_id = hall_result.data[0]["id"]
        
        # Get alerts
        result = supabase.table("alerts").select("*").eq(
            "hall_id", hall_id
        ).order("timestamp", desc=True).limit(limit).execute()
        
        return result.data if result.data else []
    except Exception as e:
        error_msg = f"Failed to get alerts for hall '{hall_name}': {e}"
        print(f"✗ {error_msg}")
        raise RuntimeError(error_msg)
