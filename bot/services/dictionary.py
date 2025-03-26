from database.repositories import UserRepository, WordRepository

class DictionaryService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.word_repo = WordRepository(db)

    def add_word(self, telegram_user, word_data):
        user = self.user_repo.get_or_create(telegram_user)
        return self.word_repo.add_word(user.id, word_data)

    def get_user_words(self, telegram_user):
        user = self.user_repo.get_or_create(telegram_user)
        return self.word_repo.get_user_words(user.id)

    def get_word_details(self, telegram_user, word_id):
        user = self.user_repo.get_or_create(telegram_user)
        return self.word_repo.get_word_by_id(word_id, user.id)

    def update_word(self, telegram_user, word_id, update_data):
        user = self.user_repo.get_or_create(telegram_user)
        return self.word_repo.update_word(word_id, user.id, update_data)

    def delete_word(self, telegram_user, word_id):
        user = self.user_repo.get_or_create(telegram_user)
        return self.word_repo.delete_word(word_id, user.id)