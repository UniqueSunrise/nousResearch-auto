import asyncio
import random
import time
import sys
import requests
from config import *

from colorama import init, Fore, Style
init(autoreset=True)

PROXY_FILE_PATH = "proxies.txt"


def truncate_text(text: str, max_words: int = 6) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    else:
        return " ".join(words[:max_words]) + "..."


def load_proxies(proxy_file):
    try:
        with open(proxy_file, "r", encoding="utf-8") as f:
            proxies_list = [line.strip() for line in f if line.strip()]
        if not proxies_list:
            raise FileNotFoundError(f"Файл с прокси '{proxy_file}' пустой.")
        return proxies_list
    except FileNotFoundError:
        raise
    except Exception as e:
        print(f"{Fore.RED}Ошибка при загрузке прокси: {e}{Style.RESET_ALL}")
        sys.exit(1)


def load_api_keys(api_keys_file):
    try:
        with open(api_keys_file, "r", encoding="utf-8") as f:
            keys = [line.strip() for line in f if line.strip()]
        if not keys:
            raise FileNotFoundError(f"Файл '{api_keys_file}' пустой, ключи для API не найдены.")
        return keys
    except FileNotFoundError:
        raise
    except Exception as e:
        print(f"{Fore.RED}Ошибка при загрузке ключей из файла {api_keys_file}: {e}{Style.RESET_ALL}")
        sys.exit(1)


def query_nous_api(api_key: str, prompt: str, model: str, proxy: str = None):
    url = "https://inference-api.nousresearch.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "stream": False
    }

    proxies = None
    if useProxy and proxy:
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            proxy = "http://" + proxy
        proxies = {
            "http": proxy,
            "https": proxy
        }

    response = requests.post(url, headers=headers, json=payload, proxies=proxies)
    response.raise_for_status()
    data = response.json()
    return data['choices'][0]['message']['content']


async def query_gpt(prompt: str) -> str:
    await asyncio.sleep(1)
    return "Ответ GPT на запрос: " + prompt


async def query_perplexity(prompt: str) -> str:
    await asyncio.sleep(1)
    return "Ответ Perplexity на запрос: " + prompt


async def async_query_nous(api_key: str, prompt: str, model: str, proxy: str = None):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, query_nous_api, api_key, prompt, model, proxy)


async def send_request(account_key, prompt_to_send, account_index, total_accounts, model, proxy=None):
    print(f"{Fore.GREEN}[{account_index}/{total_accounts}] Активность аккаунта №{account_index} — выполняется запрос к модели {Fore.CYAN}{model}{Style.RESET_ALL}.")
    try:
        response = await async_query_nous(account_key, prompt_to_send, model, proxy)
    except Exception as e:
        response = f"{Fore.RED}Ошибка при запросе: {e}{Style.RESET_ALL}"
    print(f"{Fore.YELLOW}[{account_index}/{total_accounts}]{Style.RESET_ALL} Промпт: {Fore.MAGENTA}{truncate_text(prompt_to_send)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[{account_index}/{total_accounts}]{Style.RESET_ALL} Ответ: {Fore.LIGHTWHITE_EX}{truncate_text(response)}{Style.RESET_ALL}")


async def worker(account_key, prompts_list, account_index, total_accounts,
                 nous_min_requests, nous_max_requests, sleep_between_requests_range,
                 models_list, proxy=None):
    num_requests = random.randint(nous_min_requests, nous_max_requests)
    proxy_info = f" с прокси {Fore.BLUE}{proxy}{Style.RESET_ALL}" if proxy else ""
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} Аккаунт №{account_index} (key start: {Fore.LIGHTYELLOW_EX}{str(account_key)[:6]}{Style.RESET_ALL}) будет делать {Fore.LIGHTCYAN_EX}{num_requests}{Style.RESET_ALL} запросов{proxy_info}.")

    for req_num in range(1, num_requests + 1):
        selected_model = random.choice(models_list)

        if use_different_ai == 1:  # Perplexity
            ai_prompt = "make ai query on some interesting topic"
            ai_response = await query_perplexity(ai_prompt)
            prompt_to_nous = ai_response
        elif use_different_ai == 2:  # GPT
            ai_prompt = "make ai query on some interesting topic"
            ai_response = await query_gpt(ai_prompt)
            prompt_to_nous = ai_response
        else:
            prompt_to_nous = random.choice(prompts_list)

        print(f"{Fore.GREEN}[{account_index}/{total_accounts}]{Style.RESET_ALL} Аккаунт №{account_index} — Запрос {Fore.CYAN}{req_num}/{num_requests}{Style.RESET_ALL} (запрос к {Fore.LIGHTCYAN_EX}{selected_model}{Style.RESET_ALL})")
        await send_request(account_key, prompt_to_nous, account_index, total_accounts, selected_model, proxy)

        if req_num < num_requests:
            if isinstance(sleep_between_requests_range, (list, tuple)) and len(sleep_between_requests_range) == 2:
                sleep_min = sleep_between_requests_range[0]
                sleep_max = sleep_between_requests_range[1]
            else:
                sleep_min = 10
                sleep_max = 50

            sleep_duration = random.uniform(sleep_min, sleep_max)
            print(f"{Fore.YELLOW}[{account_index}/{total_accounts}]{Style.RESET_ALL} Спим {Fore.LIGHTCYAN_EX}{sleep_duration:.2f}{Style.RESET_ALL} секунд перед следующим запросом аккаунта.")
            await asyncio.sleep(sleep_duration)


async def delayed_worker_start(delay_seconds, *worker_args, **worker_kwargs):
    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)
    await worker(*worker_args, **worker_kwargs)


async def main_async():
    if useProxy:
        try:
            proxies = load_proxies(PROXY_FILE_PATH)
        except FileNotFoundError:
            print(f"{Fore.RED}Ошибка: Режим useProxy=True, но файл прокси '{PROXY_FILE_PATH}' не найден или пустой. Завершаем работу.{Style.RESET_ALL}")
            sys.exit(1)
    else:
        proxies = []

    try:
        keys = load_api_keys("api_keys.txt")
    except FileNotFoundError:
        print(f"{Fore.RED}Ошибка: Файл с API ключами 'api_keys.txt' не найден или пустой. Завершаем работу.{Style.RESET_ALL}")
        sys.exit(1)

    total_keys = len(keys)
    indices = list(range(total_keys))
    if shuffle_wallet:
        random.shuffle(indices)

    try:
        with open('default_prompts_to_nous.txt', 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}Ошибка при загрузке файлов с промптами: {e}{Style.RESET_ALL}")
        sys.exit(1)

    for start_idx in range(0, total_keys, wallets_in_work):
        end_idx = min(start_idx + wallets_in_work, total_keys)
        batch_indices = indices[start_idx:end_idx]

        running_tasks = []
        for pos_in_batch, original_idx in enumerate(batch_indices):
            key = keys[original_idx]
            real_index = original_idx + 1  # 1-based индекс аккаунта

            prompt_list_for_worker = prompts if use_different_ai == 0 else None
            proxy_for_account = proxies[real_index - 1] if useProxy and len(proxies) >= real_index else None

            delay = pos_in_batch * sleep_between_work

            if delay == 0:
                print(f"{Fore.YELLOW}[{real_index}/{total_keys}] Запускаем аккаунт №{real_index} (key start: {Fore.LIGHTYELLOW_EX}{str(key)[:6]}{Style.RESET_ALL}) без задержки")
            else:
                print(f"{Fore.YELLOW}[{real_index}/{total_keys}] Спим {Fore.LIGHTCYAN_EX}{delay}{Style.RESET_ALL} сек перед запуском аккаунта №{real_index} (key start: {Fore.LIGHTYELLOW_EX}{str(key)[:6]}{Style.RESET_ALL})")

            task = asyncio.create_task(delayed_worker_start(
                delay,
                key, prompt_list_for_worker, real_index, total_keys,
                nous_requests_per_account_min,
                nous_requests_per_account_max,
                sleep_between_requests,
                nous_models,
                proxy_for_account
            ))
            running_tasks.append(task)

        await asyncio.gather(*running_tasks)

    print(f"{Fore.GREEN}\n=== Все задачи в асинхронном режиме выполнены ===\n{Style.RESET_ALL}")


def main_sync():
    if useProxy:
        try:
            proxies = load_proxies(PROXY_FILE_PATH)
        except FileNotFoundError:
            print(f"{Fore.RED}Ошибка: Режим useProxy=True, но файл прокси '{PROXY_FILE_PATH}' не найден или пустой. Завершаем работу.{Style.RESET_ALL}")
            sys.exit(1)
    else:
        proxies = []

    try:
        keys = load_api_keys("api_keys.txt")
    except FileNotFoundError:
        print(f"{Fore.RED}Ошибка: Файл с API ключами 'api_keys.txt' не найден или пустой. Завершаем работу.{Style.RESET_ALL}")
        sys.exit(1)

    if shuffle_wallet:
        keys_shuffled = keys[:]
        random.shuffle(keys_shuffled)
    else:
        keys_shuffled = keys

    try:
        with open("default_prompts_to_nous.txt", "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}Ошибка при загрузке файлов с промптами: {e}{Style.RESET_ALL}")
        sys.exit(1)

    total_keys = len(keys_shuffled)

    for idx, key in enumerate(keys_shuffled, start=1):
        proxy_for_account = proxies[idx - 1] if useProxy and len(proxies) >= idx else None

        if use_different_ai == 0:
            prompt = random.choice(prompts)
            num_requests = random.randint(nous_requests_per_account_min, nous_requests_per_account_max)
            proxy_info = f" с прокси {proxy_for_account}" if proxy_for_account else ""
            print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} Аккаунт №{idx} (key start: {Fore.LIGHTYELLOW_EX}{str(key)[:6]}{Style.RESET_ALL}) будет делать {Fore.LIGHTCYAN_EX}{num_requests}{Style.RESET_ALL} запросов{proxy_info}.")

            for req_num in range(1, num_requests + 1):
                selected_model = random.choice(nous_models)
                print(f"{Fore.GREEN}[{idx}/{total_keys}]{Style.RESET_ALL} Аккаунт №{idx} — Запрос {Fore.CYAN}{req_num}/{num_requests}{Style.RESET_ALL} (запрос к {Fore.LIGHTCYAN_EX}{selected_model}{Style.RESET_ALL})")
                try:
                    response = query_nous_api(key, prompt, selected_model, proxy=proxy_for_account)
                except Exception as e:
                    response = f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}"

                print(f"{Fore.YELLOW}[{idx}/{total_keys}]{Style.RESET_ALL} Промпт: {Fore.MAGENTA}{truncate_text(prompt)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[{idx}/{total_keys}]{Style.RESET_ALL} Ответ: {Fore.LIGHTWHITE_EX}{truncate_text(response)}{Style.RESET_ALL}")

                if req_num < num_requests:
                    if isinstance(sleep_between_requests, (list, tuple)) and len(sleep_between_requests) == 2:
                        sleep_min = sleep_between_requests[0]
                        sleep_max = sleep_between_requests[1]
                    else:
                        sleep_min = 10
                        sleep_max = 50
                    sleep_duration = random.uniform(sleep_min, sleep_max)
                    print(f"{Fore.YELLOW}[{idx}/{total_keys}]{Style.RESET_ALL} Спим {Fore.LIGHTCYAN_EX}{sleep_duration:.2f}{Style.RESET_ALL} секунд перед следующим запросом")
                    time.sleep(sleep_duration)
        else:
            print(f"{Fore.RED}Синхронный режим не поддерживает use_different_ai != 0. use_different_ai={use_different_ai}{Style.RESET_ALL}")
            break

        sleep_time = sleep_between_work * ((idx - 1) % wallets_in_work)
        print(f"{Fore.YELLOW}[{idx}/{total_keys}]{Style.RESET_ALL} Спим {sleep_time} секунд перед следующим аккаунтом")
        time.sleep(sleep_time)

    print(f"{Fore.GREEN}\n=== Работа завершена ===\n{Style.RESET_ALL}")


if __name__ == "__main__":
    if async_sync_work == 1:
        asyncio.run(main_async())
    else:
        main_sync()
