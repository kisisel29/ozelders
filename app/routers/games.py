from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import random
import time
from ..deps.firebase import require_student, verify_token
from ..models.schemas import GameResult
from ..repos.users import UsersRepository
from google.cloud import firestore
from datetime import datetime

router = APIRouter()

@router.get("/available")
async def get_available_games():
    """Get list of available educational games"""
    return {
        "games": [
            {
                "id": "times-table-sprint",
                "name": "Çarpım Tablosu Sprint",
                "description": "Çarpım tablosunu hızlıca çöz!",
                "grade_level": "5-8",
                "subject": "Matematik",
                "difficulty": "Orta"
            },
            {
                "id": "math-puzzle",
                "name": "Matematik Bulmaca",
                "description": "Sayıları kullanarak hedef sayıya ulaş!",
                "grade_level": "6-8",
                "subject": "Matematik",
                "difficulty": "Zor"
            },
            {
                "id": "fraction-fun",
                "name": "Kesir Eğlencesi",
                "description": "Kesirleri karşılaştır ve sırala!",
                "grade_level": "5-7",
                "subject": "Matematik",
                "difficulty": "Kolay"
            }
        ]
    }

@router.get("/times-table-sprint/questions")
async def get_times_table_questions(difficulty: str = "medium"):
    """Generate times table questions for the sprint game"""
    questions = []
    
    if difficulty == "easy":
        # 1-5 times tables
        for i in range(10):
            a = random.randint(1, 5)
            b = random.randint(1, 10)
            questions.append({
                "id": f"q{i+1}",
                "question": f"{a} × {b} = ?",
                "answer": a * b,
                "options": [
                    a * b,
                    a * b + random.randint(1, 5),
                    a * b - random.randint(1, 3),
                    a * b + random.randint(-2, 2)
                ]
            })
    elif difficulty == "medium":
        # 1-10 times tables
        for i in range(15):
            a = random.randint(1, 10)
            b = random.randint(1, 12)
            questions.append({
                "id": f"q{i+1}",
                "question": f"{a} × {b} = ?",
                "answer": a * b,
                "options": [
                    a * b,
                    a * b + random.randint(1, 8),
                    a * b - random.randint(1, 5),
                    a * b + random.randint(-3, 3)
                ]
            })
    else:  # hard
        # 1-12 times tables with larger numbers
        for i in range(20):
            a = random.randint(1, 12)
            b = random.randint(1, 15)
            questions.append({
                "id": f"q{i+1}",
                "question": f"{a} × {b} = ?",
                "answer": a * b,
                "options": [
                    a * b,
                    a * b + random.randint(1, 10),
                    a * b - random.randint(1, 7),
                    a * b + random.randint(-4, 4)
                ]
            })
    
    # Shuffle options for each question
    for question in questions:
        random.shuffle(question["options"])
    
    return {"questions": questions}

@router.get("/math-puzzle/questions")
async def get_math_puzzle_questions():
    """Generate math puzzle questions"""
    puzzles = []
    
    for i in range(5):
        # Generate target number and available numbers
        target = random.randint(20, 100)
        numbers = [random.randint(1, 9) for _ in range(4)]
        
        puzzles.append({
            "id": f"puzzle{i+1}",
            "target": target,
            "numbers": numbers,
            "description": f"Bu sayıları kullanarak {target} sayısına ulaşın: {', '.join(map(str, numbers))}"
        })
    
    return {"puzzles": puzzles}

@router.get("/fraction-fun/questions")
async def get_fraction_questions():
    """Generate fraction comparison questions"""
    questions = []
    
    for i in range(10):
        # Generate two fractions
        num1 = random.randint(1, 9)
        den1 = random.randint(2, 10)
        num2 = random.randint(1, 9)
        den2 = random.randint(2, 10)
        
        # Calculate decimal values
        val1 = num1 / den1
        val2 = num2 / den2
        
        if val1 > val2:
            answer = ">"
        elif val1 < val2:
            answer = "<"
        else:
            answer = "="
        
        questions.append({
            "id": f"frac{i+1}",
            "fraction1": f"{num1}/{den1}",
            "fraction2": f"{num2}/{den2}",
            "answer": answer,
            "options": [">", "<", "="]
        })
    
    return {"questions": questions}

@router.post("/submit-result")
async def submit_game_result(
    game_name: str,
    score: int,
    max_score: int,
    time_taken: int,
    user: dict = Depends(verify_token)
):
    """Submit game result for analytics"""
    try:
        db = firestore.client()
        game_results_collection = db.collection('game_results')
        
        # Create game result document
        result_doc = {
            "game_name": game_name,
            "score": score,
            "max_score": max_score,
            "time_taken": time_taken,
            "student_uid": user['uid'],
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = game_results_collection.add(result_doc)
        
        return {
            "message": "Oyun sonucu kaydedildi!",
            "result_id": doc_ref[1].id,
            "percentage": round((score / max_score) * 100, 1)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save game result: {str(e)}")

@router.get("/leaderboard/{game_name}")
async def get_game_leaderboard(game_name: str, limit: int = 10):
    """Get leaderboard for a specific game"""
    try:
        db = firestore.client()
        game_results_collection = db.collection('game_results')
        
        # Query for the specific game, ordered by score descending
        query = game_results_collection.where("game_name", "==", game_name).order_by("score", direction=firestore.Query.DESCENDING).limit(limit)
        
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            
            # Get student name
            users_repo = UsersRepository()
            student = await users_repo.get_user(data['student_uid'])
            data['student_name'] = student.display_name if student else "Bilinmeyen Öğrenci"
            
            # Calculate percentage
            data['percentage'] = round((data['score'] / data['max_score']) * 100, 1)
            
            results.append(data)
        
        return {
            "game_name": game_name,
            "leaderboard": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get leaderboard: {str(e)}")

@router.get("/my-stats")
async def get_my_game_stats(user: dict = Depends(verify_token)):
    """Get current user's game statistics"""
    try:
        db = firestore.client()
        game_results_collection = db.collection('game_results')
        
        # Query for user's game results
        query = game_results_collection.where("student_uid", "==", user['uid'])
        
        results = []
        total_games = 0
        total_score = 0
        total_max_score = 0
        
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            data['percentage'] = round((data['score'] / data['max_score']) * 100, 1)
            
            results.append(data)
            total_games += 1
            total_score += data['score']
            total_max_score += data['max_score']
        
        # Calculate averages
        avg_score = total_score / total_games if total_games > 0 else 0
        avg_percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0
        
        # Group by game
        game_stats = {}
        for result in results:
            game_name = result['game_name']
            if game_name not in game_stats:
                game_stats[game_name] = {
                    "games_played": 0,
                    "total_score": 0,
                    "total_max_score": 0,
                    "best_score": 0,
                    "average_percentage": 0
                }
            
            game_stats[game_name]["games_played"] += 1
            game_stats[game_name]["total_score"] += result['score']
            game_stats[game_name]["total_max_score"] += result['max_score']
            game_stats[game_name]["best_score"] = max(game_stats[game_name]["best_score"], result['score'])
        
        # Calculate averages for each game
        for game_name, stats in game_stats.items():
            stats["average_percentage"] = round((stats["total_score"] / stats["total_max_score"] * 100), 1)
        
        return {
            "total_games_played": total_games,
            "average_score": round(avg_score, 1),
            "average_percentage": round(avg_percentage, 1),
            "game_stats": game_stats,
            "recent_results": results[-5:]  # Last 5 games
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get game stats: {str(e)}")