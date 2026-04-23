
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

def get_or_create_profile(user):
    """Получить или создать профиль пользователя"""
    profile, created = Profile.objects.get_or_create(user=user)
    return profile


def get_profile(user_id):
    """Получение профиля пользователя через ORM"""
    from django.contrib.auth.models import User

    try:
        user = User.objects.get(id=user_id)
        profile, created = Profile.objects.get_or_create(user=user)

        return {
            'username': user.username,
            'nickname': profile.nickname or '',
            'age': profile.age,
            'school': profile.school or '',
            'grade': profile.grade or '',
            'main_subject': profile.main_subject,
            'hobby': profile.hobby or '',
            'avatar': profile.avatar.url if profile.avatar else None,
            'is_guest': profile.is_guest,
        }
    except User.DoesNotExist:
        return None

def save_profile(user_id, username, data):
    """Сохранить профиль"""
    user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(user=user)

    profile.nickname = data.get('nickname', '')
    profile.age = data.get('age')
    profile.school = data.get('school', '')
    profile.grade = data.get('grade', '')
    profile.main_subject = data.get('main_subject', 'physics')
    profile.hobby = data.get('hobby', '')
    if data.get('avatar'):
        profile.avatar = data.get('avatar')
    profile.save()
    return True


# ========== ВОПРОСЫ ==========

def create_question(user_id, title, content, subject='general'):
    user = get_object_or_404(User, id=user_id)
    question = Question.objects.create(
        user=user,
        title=title,
        content=content,
        subject=subject
    )
    # Добавляем активность
    UserActivity.objects.create(
        user=user,
        activity_type='ask_question',
        question=question
    )
    return question.id


def get_recent_questions(limit=10):
    questions = Question.objects.filter(is_deleted=False).order_by('-created_at')[:limit]
    result = []
    for q in questions:
        result.append({
            'id': q.id,
            'title': q.title,
            'content': q.content,
            'subject': q.subject,
            'created_at': q.created_at,
            'user_id': q.user.id,
            'author_name': q.author_name(),
            'answers_count': q.answers_count()
        })
    return result


def get_question_by_id(question_id):
    try:
        q = Question.objects.get(id=question_id, is_deleted=False)
        return {
            'id': q.id,
            'title': q.title,
            'content': q.content,
            'subject': q.subject,
            'created_at': q.created_at,
            'user_id': q.user.id,
            'author_name': q.author_name()
        }
    except Question.DoesNotExist:
        return None


# ========== ОТВЕТЫ ==========

def create_answer(user_id, question_id, content):
    user = get_object_or_404(User, id=user_id)
    question = get_object_or_404(Question, id=question_id)
    answer = Answer.objects.create(
        user=user,
        question=question,
        content=content
    )
    # Добавляем активность
    UserActivity.objects.create(
        user=user,
        activity_type='answer_question',
        question=question,
        answer=answer
    )
    return answer.id


def get_answers_for_question(question_id, user_id=None):
    answers = Answer.objects.filter(question_id=question_id, is_deleted=False).order_by('created_at')
    result = []
    for a in answers:
        answer_data = {
            'id': a.id,
            'content': a.content,
            'created_at': a.created_at,
            'user_id': a.user.id,
            'author_name': a.author_name(),
            'likes': a.likes_count(),
            'dislikes': a.dislikes_count(),
            'user_rating': None
        }

        if user_id:
            try:
                rating = AnswerRating.objects.get(user_id=user_id, answer_id=a.id)
                answer_data['user_rating'] = 'like' if rating.rating == 1 else 'dislike'
            except AnswerRating.DoesNotExist:
                pass

        result.append(answer_data)
    return result


def rate_answer(user_id, answer_id, rating):
    user = get_object_or_404(User, id=user_id)
    answer = get_object_or_404(Answer, id=answer_id)

    rating_obj, created = AnswerRating.objects.get_or_create(
        user=user,
        answer=answer,
        defaults={'rating': rating}
    )

    if not created:
        if rating_obj.rating == rating:
            rating_obj.delete()
        else:
            rating_obj.rating = rating
            rating_obj.save()

    # Добавляем активность
    UserActivity.objects.create(
        user=user,
        activity_type='rate_answer',
        answer=answer
    )
    return True


# ========== ЖАЛОБЫ ==========

def create_complaint(user_id, complaint_type, reason, question_id=None, answer_id=None):
    user = get_object_or_404(User, id=user_id)
    complaint = Complaint.objects.create(
        user=user,
        complaint_type=complaint_type,
        reason=reason
    )
    if question_id:
        complaint.question_id = question_id
    if answer_id:
        complaint.answer_id = answer_id
    complaint.save()

    # Добавляем активность
    UserActivity.objects.create(
        user=user,
        activity_type='complaint',
        question_id=question_id,
        answer_id=answer_id,
        metadata=complaint_type
    )
    return complaint.id


def get_all_complaints(resolved=False):
    return Complaint.objects.filter(is_resolved=resolved).order_by('-created_at')


def resolve_complaint(complaint_id, moderator_id):
    Complaint.objects.filter(id=complaint_id).update(is_resolved=True)


# ========== АКТИВНОСТЬ ==========

def add_activity(user_id, activity_type, question_id=None, answer_id=None, metadata=None):
    user = get_object_or_404(User, id=user_id)
    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        question_id=question_id,
        answer_id=answer_id,
        metadata=metadata
    )


def get_user_activities(user_id, limit=50):
    return UserActivity.objects.filter(user_id=user_id).order_by('-created_at')[:limit]


# ========== НАСТРОЙКИ ==========

def get_user_settings(user_id):
    user = get_object_or_404(User, id=user_id)
    settings, created = UserSettings.objects.get_or_create(user=user)
    return {
        'theme': settings.theme,
        'notifications': settings.notifications,
        'language': settings.language
    }


def update_user_settings(user_id, settings):
    user = get_object_or_404(User, id=user_id)
    user_settings, created = UserSettings.objects.get_or_create(user=user)
    user_settings.theme = settings.get('theme', 'light')
    user_settings.notifications = settings.get('notifications', True)
    user_settings.language = settings.get('language', 'ru')
    user_settings.save()


# ========== ИИ ЧАТ ==========

def save_ai_chat(user_id, question, answer):
    user = get_object_or_404(User, id=user_id)
    AIChatHistory.objects.create(
        user=user,
        question=question,
        answer=answer
    )


# ========== УДАЛЕНИЕ ==========

def delete_question(question_id, moderator_id):
    Question.objects.filter(id=question_id).update(is_deleted=True)


def delete_answer(answer_id, moderator_id):
    Answer.objects.filter(id=answer_id).update(is_deleted=True)

class Profile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    school = models.CharField(max_length=200, blank=True, null=True)
    grade = models.CharField(max_length=20, blank=True, null=True)

    SUBJECT_CHOICES = [
        ('math', '📐 Математика'),
        ('physics', '⚡ Физика'),
        ('chemistry', '🧪 Химия'),
        ('biology', '🧬 Биология'),
        ('history', '📜 История'),
        ('literature', '📖 Литература'),
        ('programming', '💻 Кодинг'),
        ('general', '📚 Общий'),
    ]
    main_subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='physics')
    hobby = models.CharField(max_length=200, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_guest = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname or self.user.username


class Question(models.Model):
    """Вопрос пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=200)
    content = models.TextField()

    SUBJECT_CHOICES = [
        ('math', '📐 Математика'),
        ('physics', '⚡ Физика'),
        ('chemistry', '🧪 Химия'),
        ('biology', '🧬 Биология'),
        ('history', '📜 История'),
        ('literature', '📖 Литература'),
        ('programming', '💻 Программирование'),
        ('general', '💬 Общий'),
    ]
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def answers_count(self):
        return self.answers.filter(is_deleted=False).count()

    def author_name(self):
        if hasattr(self.user, 'profile') and self.user.profile.nickname:
            return self.user.profile.nickname
        return self.user.username


class Answer(models.Model):
    """Ответ на вопрос"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Ответ на {self.question.title}"

    def author_name(self):
        if hasattr(self.user, 'profile') and self.user.profile.nickname:
            return self.user.profile.nickname
        return self.user.username

    def likes_count(self):
        return self.ratings.filter(rating=1).count()

    def dislikes_count(self):
        return self.ratings.filter(rating=0).count()


class AnswerRating(models.Model):
    """Оценка ответа"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_ratings')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(1, 'Like'), (0, 'Dislike')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'answer']

    def __str__(self):
        return f"{self.user.username} оценил ответ {self.answer.id}"


class Complaint(models.Model):
    """Жалоба на вопрос или ответ"""
    COMPLAINT_TYPES = [
        ('spam', 'Спам'),
        ('offensive', 'Оскорбительное содержание'),
        ('incorrect', 'Неверная информация'),
        ('other', 'Другое'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    complaint_type = models.CharField(max_length=50, choices=COMPLAINT_TYPES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True, related_name='complaints')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True, related_name='complaints')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        target = self.question if self.question else self.answer
        return f"Жалоба от {self.user.username} на {target}"


class AIChatHistory(models.Model):
    """История чата с ИИ"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chats')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Чат с ИИ: {self.user.username} - {self.created_at}"


class UserActivity(models.Model):
    """Активность пользователя"""
    ACTIVITY_TYPES = [
        ('ask_question', 'Задал вопрос'),
        ('answer_question', 'Ответил на вопрос'),
        ('rate_answer', 'Оценил ответ'),
        ('complaint', 'Пожаловался'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    metadata = models.TextField(blank=True, null=True)  # JSON поле для доп. данных
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.activity_type}"


class UserSettings(models.Model):
    """Настройки пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=20, choices=[('light', 'Светлая'), ('dark', 'Тёмная')], default='light')
    notifications = models.BooleanField(default=True)
    language = models.CharField(max_length=10, choices=[('ru', 'Русский'), ('en', 'English')], default='ru')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Настройки {self.user.username}"