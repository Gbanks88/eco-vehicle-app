import os
import sys
import pytest
import redis
import json
from datetime import datetime, timedelta

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from web.models.recycling import RecyclingSession

@pytest.fixture
def redis_client():
    return redis.Redis(host='localhost', port=6379, db=1)  # Use db 1 for testing

@pytest.fixture
def recycling_session(redis_client):
    session = RecyclingSession(redis_client)
    yield session
    # Cleanup after tests
    redis_client.flushdb()

def test_record_recycling(recycling_session):
    user_id = "test_user"
    item_id = "aluminum_can"
    bin_id = "metal"
    score = 100.0
    
    recycling_session.record_recycling(user_id, item_id, bin_id, score)
    
    # Check if score was recorded
    assert float(recycling_session.redis.zscore('recycling_scores', user_id)) == score
    
    # Check if history was recorded
    history_key = f'recycling_history:{user_id}'
    history = recycling_session.redis.hgetall(history_key)
    assert len(history) == 1
    
    # Check if stats were updated
    stats_key = f'user_stats:{user_id}'
    stats = recycling_session.redis.hgetall(stats_key)
    assert int(stats[b'total_items']) == 1
    assert int(stats[b'items_metal']) == 1
    assert int(stats[b'total_score']) == 100

def test_calculate_score(recycling_session):
    # Test correct bin placement
    score1 = recycling_session.calculate_score('aluminum_can', 'metal', 25.0)
    assert score1 > 0
    
    # Test incorrect bin placement
    score2 = recycling_session.calculate_score('aluminum_can', 'plastic', 25.0)
    assert score2 < score1
    
    # Test time bonus
    score3 = recycling_session.calculate_score('aluminum_can', 'metal', 15.0)
    assert score3 > score1

def test_achievements(recycling_session):
    user_id = "test_user"
    
    # Add enough score to trigger achievement
    recycling_session.record_recycling(user_id, "aluminum_can", "metal", 1000)
    
    # Check if achievement was awarded
    achievements = recycling_session.check_achievements(user_id, 1000)
    assert "recycling_novice" in achievements
    
    # Check if achievement is stored
    stored_achievements = recycling_session.redis.smembers(f'achievements:{user_id}')
    assert b"recycling_novice" in stored_achievements

def test_leaderboard(recycling_session):
    # Add multiple users with different scores
    users = [
        ("user1", 100),
        ("user2", 200),
        ("user3", 150)
    ]
    
    for user_id, score in users:
        recycling_session.record_recycling(user_id, "aluminum_can", "metal", score)
    
    # Get leaderboard
    leaderboard = recycling_session.get_leaderboard(10)
    
    # Check order
    assert len(leaderboard) == 3
    assert leaderboard[0]['user_id'] == "user2"
    assert leaderboard[0]['score'] == 200
    assert leaderboard[1]['user_id'] == "user3"
    assert leaderboard[2]['user_id'] == "user1"

def test_cleanup_old_data(recycling_session):
    user_id = "test_user"
    
    # Add some old data
    old_time = (datetime.now() - timedelta(days=31)).isoformat()
    recycling_session.redis.hset(
        f'recycling_history:{user_id}',
        old_time,
        json.dumps({
            'item_id': 'aluminum_can',
            'bin_id': 'metal',
            'score': 100,
            'timestamp': old_time
        })
    )
    
    # Add some recent data
    recycling_session.record_recycling(user_id, "aluminum_can", "metal", 100)
    
    # Run cleanup
    recycling_session.cleanup_old_data(30)
    
    # Check if old data was removed but new data remains
    history = recycling_session.redis.hgetall(f'recycling_history:{user_id}')
    assert len(history) == 1
    
    # Verify the remaining entry is the recent one
    entry = json.loads(list(history.values())[0].decode())
    assert datetime.fromisoformat(entry['timestamp']) > datetime.now() - timedelta(days=30)
