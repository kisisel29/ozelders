from typing import Dict, Any, Tuple, List

class ScoringService:
    @staticmethod
    def score_submission(answers: Dict[str, Any], answer_schema: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score a student submission based on the answer schema
        Returns (score, breakdown)
        """
        total_score = 0
        max_score = len(answer_schema)
        breakdown = {}
        
        for question_id, student_answer in answers.items():
            if question_id not in answer_schema:
                continue
                
            schema = answer_schema[question_id]
            question_score = 0
            feedback = ""
            
            if schema['type'] == 'mcq':
                # Multiple choice - exact match
                if student_answer == schema['answer']:
                    question_score = 1
                    feedback = "Doğru!"
                else:
                    feedback = f"Yanlış. Doğru cevap: {schema['answer']}"
                    
            elif schema['type'] == 'numeric':
                # Numeric with tolerance
                try:
                    student_num = float(student_answer)
                    correct_num = float(schema['answer'])
                    tolerance = float(schema.get('tolerance', 0))
                    
                    if abs(student_num - correct_num) <= tolerance:
                        question_score = 1
                        feedback = "Doğru!"
                    else:
                        feedback = f"Yanlış. Doğru cevap: {schema['answer']}"
                except (ValueError, TypeError):
                    feedback = "Geçersiz sayısal değer"
                    
            elif schema['type'] == 'short':
                # Short answer - keyword matching
                if isinstance(student_answer, str) and isinstance(schema['answer'], str):
                    student_lower = student_answer.lower().strip()
                    correct_lower = schema['answer'].lower().strip()
                    
                    # Check for exact match first
                    if student_lower == correct_lower:
                        question_score = 1
                        feedback = "Mükemmel!"
                    else:
                        # Check for keyword matching
                        keywords = schema.get('keywords', [])
                        if keywords:
                            student_words = set(student_lower.split())
                            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in student_words)
                            if keyword_matches >= len(keywords) * 0.7:  # 70% keyword match
                                question_score = 0.8
                                feedback = "İyi, ancak daha detaylı olabilir"
                            else:
                                feedback = f"Eksik. Anahtar kelimeler: {', '.join(keywords)}"
                        else:
                            feedback = f"Yanlış. Doğru cevap: {schema['answer']}"
                else:
                    feedback = "Geçersiz cevap formatı"
                    
            elif schema['type'] == 'checkbox':
                # Checkbox - multiple correct answers
                if isinstance(student_answer, list) and isinstance(schema['answer'], list):
                    student_set = set(student_answer)
                    correct_set = set(schema['answer'])
                    
                    if student_set == correct_set:
                        question_score = 1
                        feedback = "Tüm doğru seçenekler işaretlendi!"
                    else:
                        # Partial credit for some correct answers
                        correct_checked = len(student_set.intersection(correct_set))
                        incorrect_checked = len(student_set - correct_set)
                        missed_correct = len(correct_set - student_set)
                        
                        if correct_checked > 0 and incorrect_checked == 0:
                            question_score = 0.5
                            feedback = f"Bazı doğru seçenekler işaretlendi ({correct_checked}/{len(correct_set)})"
                        else:
                            feedback = f"Yanlış seçimler var. Doğru cevaplar: {', '.join(schema['answer'])}"
                else:
                    feedback = "Geçersiz cevap formatı"
            
            breakdown[question_id] = {
                'score': question_score,
                'feedback': feedback,
                'student_answer': student_answer,
                'correct_answer': schema['answer']
            }
            
            total_score += question_score
        
        return total_score, breakdown
    
    @staticmethod
    def generate_feedback(breakdown: Dict[str, Any], score: float, max_score: float) -> str:
        """Generate overall feedback based on score breakdown"""
        if score == max_score:
            return "Mükemmel! Tüm soruları doğru cevapladın! 🎉"
        elif score >= max_score * 0.8:
            return "Çok iyi! Neredeyse mükemmel! 👍"
        elif score >= max_score * 0.6:
            return "İyi! Biraz daha çalışarak daha iyi sonuçlar alabilirsin. 💪"
        elif score >= max_score * 0.4:
            return "Orta seviye. Konuyu tekrar gözden geçirmen faydalı olacak. 📚"
        else:
            return "Bu konuyu tekrar çalışman gerekiyor. Sorularını öğretmenine sorabilirsin. 🤔"
    
    @staticmethod
    def calculate_percentage(score: float, max_score: float) -> float:
        """Calculate percentage score"""
        if max_score == 0:
            return 0
        return (score / max_score) * 100
    
    @staticmethod
    def get_grade_level(percentage: float) -> str:
        """Get grade level based on percentage"""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"