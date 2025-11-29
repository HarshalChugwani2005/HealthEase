import urllib.parse
import logging

logger = logging.getLogger(__name__)

def get_direct_connection_url(original_url: str) -> str:
    """
    Constructs a direct connection URL for MongoDB Atlas fallback.
    Extracts credentials from the original URL and uses known shard hosts.
    """
    try:
        # Parse the original URL to get credentials
        parsed = urllib.parse.urlparse(original_url)
        
        # Extract username and password
        username = parsed.username
        password = parsed.password
        
        if not username or not password:
            logger.warning("Could not extract credentials from MongoDB URL")
            return None
            
        # Known shard hosts for this cluster
        shards = [
            "ac-w3wf0g5-shard-00-00.a4dssr7.mongodb.net:27017",
            "ac-w3wf0g5-shard-00-01.a4dssr7.mongodb.net:27017",
            "ac-w3wf0g5-shard-00-02.a4dssr7.mongodb.net:27017"
        ]
        
        hosts_str = ",".join(shards)
        
        # Construct direct connection string
        # replicaSet=atlas-12fv4m-shard-0
        # ssl=true
        # authSource=admin
        
        direct_url = (
            f"mongodb://{username}:{password}@{hosts_str}/healthease"
            f"?ssl=true&replicaSet=atlas-12fv4m-shard-0&authSource=admin&tlsInsecure=true"
        )
        
        return direct_url
        
    except Exception as e:
        logger.error(f"Error constructing direct MongoDB URL: {e}")
        return None
