"""Клиент Groq для ответов модели."""

from collections.abc import AsyncIterator

from groq import AsyncGroq, Groq

SYSTEM_PROMPT = """Тебя зовут Qubit. Ты умный помощник в Telegram.

Формат ответов — HTML в стиле Telegram Bot API (parse_mode HTML). Используй структуру и оформление:
— абзацы и пустые строки между блоками,
— ключевые мысли выделяй <b>...</b>,
— пояснения и термины — <i>...</i>,
— короткий код в строке — <code>...</code>,
— многострочный код или пример команд — только в <pre>...</pre>,
— если даёшь ссылку — <a href="https://example.com">текст ссылки</a>.

Строго: не ставь необработанные символы < и > как «сырой» текст вне тегов.

Не добавляй в конце подпись, логотип или «ответил Qubit» — это добавляет клиент Telegram автоматически.

Отвечай подробно и по делу; если не знаешь — признайся и предложи, как узнать."""


class GroqService:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = Groq(api_key=api_key)
        self._aclient = AsyncGroq(api_key=api_key)
        self._model = model

    @staticmethod
    def _build_messages(
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages

    def complete_sync(
        self,
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=self._build_messages(user_message, history),
            temperature=0.7,
            max_tokens=4096,
        )
        choice = completion.choices[0]
        content = choice.message.content
        if not content:
            return "Не удалось получить ответ от модели. Попробуйте ещё раз."
        return content.strip()

    async def stream_complete(
        self,
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncIterator[str]:
        stream = await self._aclient.chat.completions.create(
            model=self._model,
            messages=self._build_messages(user_message, history),
            temperature=0.7,
            max_tokens=4096,
            stream=True,
        )

        acc = ""
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            if not delta:
                continue
            acc += delta
            yield acc
