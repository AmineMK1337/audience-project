"""Question schema and database operations."""
from app.services.firestore import get_firestore_client
from datetime import datetime

def save_question(name: str, question: str):
    """Save audience question to Firestore database"""
    db = get_firestore_client()
    
    # Add question to database
    doc_ref = db.collection('questions').add({
        'name': name,
        'question': question,
        'timestamp': datetime.now(),
        'answered': False
    })
    print(f"Question saved with ID: {doc_ref[1].id}")
    return doc_ref[1].id

def get_recent_questions(limit: int = 50):
    """Get recent questions for presenter dashboard"""
    db = get_firestore_client()
    
    docs = db.collection('questions').order_by('timestamp', direction='DESCENDING').limit(limit).get()
    
    questions = []
    for doc in docs:
        data = doc.to_dict()
        questions.append({
            'id': doc.id,
            'name': data['name'],
            'question': data['question'],
            'timestamp': data['timestamp'],
            'answered': data.get('answered', False)
        })
    
    return questions

def mark_question_answered(question_id: str):
    """Mark question as answered"""
    db = get_firestore_client()
    db.collection('questions').document(question_id).update({'answered': True})