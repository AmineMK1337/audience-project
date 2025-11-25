import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.firestore import get_firestore_client
from datetime import datetime
from typing import Literal

# Define valid reaction types
ReactionType = Literal["speed_up", "slow_down", "im_lost", "good_pace"]

def save_reaction(name: str, reaction: ReactionType):
    """Save audience reaction to Firestore database"""
    db = get_firestore_client()
    
    # Add reaction to database
    doc_ref = db.collection('reactions').add({
        'name': name,
        'reaction': reaction,
        'timestamp': datetime.now()
    })
    print(f"Reaction saved with ID: {doc_ref[1].id}")
    return doc_ref[1].id

def get_recent_reactions(limit: int = 50):
    """Get recent reactions for presenter dashboard"""
    db = get_firestore_client()
    
    docs = db.collection('reactions').order_by('timestamp', direction='DESCENDING').limit(limit).get()
    
    reactions = []
    for doc in docs:
        data = doc.to_dict()
        reactions.append({
            'id': doc.id,
            'name': data['name'],
            'reaction': data['reaction'],
            'timestamp': data['timestamp']
        })
    
    return reactions

def test_reactions():
    # Test saving different reactions
    save_reaction("Tarek", "speed_up")
    save_reaction("Ayoub", "slow_down") 
    save_reaction("Youssef", "im_lost")
    save_reaction("Anas", "good_pace")
    
    # Get and display recent reactions
    reactions = get_recent_reactions()
    print(f"\nRecent reactions ({len(reactions)} total):")
    for reaction in reactions:
        print(f"- {reaction['name']}: {reaction['reaction']} at {reaction['timestamp']}")

if __name__ == "__main__":
    test_reactions()