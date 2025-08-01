# Soft settings
use_different_ai = 0  # 0 - свой prompt в Nous; 1 - Perplexity; 2 - GPT
async_sync_work = 0   # 0 - синхронный режим, 1 - асинхронный
wallets_in_work = 5   # количество параллельных аккаунтов
sleep_between_work = 50  # пауза между аккаунтами (в секундах) с нарастанием
shuffle_wallet = False  # перемешивать ключи перед запуском
useProxy = False # True - использовать, False - не использовать

nous_requests_per_account_min = 3  # минимальное количество запросов к Nous на аккаунт за запуск
nous_requests_per_account_max = 25  # максимальное количество запросов к Nous на аккаунт за запуск
sleep_between_requests = [30, 60]  # задержка (сек) между запросами одного аккаунта

api_gpt_key = ""         # GPT API ключ
api_perplexity = ""      # Perplexity API ключ

'''
Что такое токены?
Токен — это единица текста, на которую модель разбивает вход и выход. 
Один токен может быть примерно 3/4 слова на английском 
Обычно 1 токен ≈ 4 символам (но это очень приблизительно, зависит от языка и структуры слов).
'''
max_tokens = 5000 # максимальное количество токенов в ответе от модели Nous Research

'''
Все модели Nous
Hermes-3-Llama-3.1-70B -- $0.90/1M tokens
DeepHermes-3-Llama-3-8B-Preview -- $0.70/1M tokens
DeepHermes-3-Mistral-24B-Preview -- $0.85/1M tokens
Hermes-3-Llama-3.1-405B -- $1.80/1M tokens
'''
# список моделей Nous Research для случайного выбора
nous_models = [
    "Hermes-3-Llama-3.1-70B",
    "Hermes-3-Llama-3.1-405B",
    "DeepHermes-3-Llama-3-8B-Preview",
    "DeepHermes-3-Mistral-24B-Preview",
]