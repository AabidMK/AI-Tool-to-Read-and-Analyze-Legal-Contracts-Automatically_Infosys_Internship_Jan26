import logging
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

# Constants
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "contract-clauses"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_ingestion():
    """Verify that clause ingestion was successful."""
    
    try:
        logger.info("Starting ingestion verification...")
        
        # Initialize Qdrant client
        qdrant_client = QdrantClient(url=QDRANT_URL)
        
        # 1. Check collection existence and get info
        try:
            collection_info = qdrant_client.get_collection(COLLECTION_NAME)
            points_count = collection_info.points_count
            print(f"✅ Collection '{COLLECTION_NAME}' exists")
            print(f"✅ Points count: {points_count}")
            
            if points_count == 0:
                print("❌ Collection is empty - no points found")
                return False
                
        except Exception as e:
            print(f"❌ Collection '{COLLECTION_NAME}' not found: {e}")
            return False
        
        # 2. Sample payloads using scroll
        print(f"\n📋 Sample payloads from collection:")
        print("-" * 60)
        
        scroll_result = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=3,
            with_payload=True,
            with_vectors=False
        )
        
        points = scroll_result[0]
        if not points:
            print("❌ No points found in scroll results")
            return False
        
        for i, point in enumerate(points, 1):
            payload = point.payload
            metadata = payload.get('metadata', {})
            print(f"\nPoint {i} (ID: {point.id}):")
            print(f"  Contract Type: {metadata.get('contract_type', 'N/A')}")
            print(f"  Clause Title: {metadata.get('clause_title', 'N/A')}")
            print(f"  Jurisdiction: {metadata.get('jurisdiction', 'N/A')}")
            print(f"  Version: {metadata.get('version', 'N/A')}")
            print(f"  Last Updated: {metadata.get('last_updated', 'N/A')}")
            print(f"  Source: {metadata.get('source', 'N/A')}")
        
        print(f"\n✅ Verification completed successfully!")
        print(f"✅ Collection has {points_count} points with valid payloads")
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main verification function."""
    success = verify_ingestion()
    if not success:
        exit(1)

if __name__ == "__main__":
    main()
