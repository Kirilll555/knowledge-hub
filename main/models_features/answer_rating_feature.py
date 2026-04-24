from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q
from .question_feature import Question


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ответ на вопрос #{self.question_id}"


class AnswerRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='ratings')
    is_like = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'answer']


def create_answer(user_id, question_id, content):
    return Answer.objects.create(
        user_id=user_id,
        question_id=question_id,
        content=content
    ).id


def get_answers_for_question(question_id, user_id=None):
    answers = Answer.objects.filter(
        question_id=question_id,
        is_deleted=False
    ).select_related('user__profile').order_by('created_at')

    result = []
    for a in answers:
        ratings = a.ratings.aggregate(
            likes=Count('id', filter=models.Q(is_like=True)),
            dislikes=Count('id', filter=models.Q(is_like=False))
        )

        answer_data = {
            'id': a.id,
            'content': a.content,
            'created_at': a.created_at,
            'user_id': a.user.id,
            'author_name': a.user.profile.nickname or a.user.username,
            'likes': ratings['likes'],
            'dislikes': ratings['dislikes'],
            'user_rating': None
        }

        if user_id:
            user_rating = AnswerRating.objects.filter(user_id=user_id, answer_id=a.id).first()
            if user_rating:
                answer_data['user_rating'] = 'like' if user_rating.is_like else 'dislike'

        result.append(answer_data)

    return result


def delete_answer(answer_id, moderator_id):
    Answer.objects.filter(id=answer_id).update(is_deleted=True)


def rate_answer(user_id, answer_id, rating):
    is_like = rating == 1
    rating_obj, created = AnswerRating.objects.get_or_create(
        user_id=user_id,
        answer_id=answer_id,
        defaults={'is_like': is_like}
    )

    if not created and rating_obj.is_like != is_like:
        rating_obj.is_like = is_like
        rating_obj.save()
    elif not created:
        rating_obj.delete()

    return True
