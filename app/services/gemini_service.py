import time

from google import genai

from app.core.config import Settings


class GeminiService:

    def __init__(
        self,
        settings: Settings,
    ):
        self.settings = settings

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.max_retries = 3

    def generate(
        self,
        prompt: str,
        model: str,
    ) -> tuple[str, str]:

        try:
            answer = self._generate_with_retry(
                prompt=prompt,
                model=model,
            )

            return answer, model

        except Exception as primary_error:

            # Try fallback model
            if model != self.settings.fallback_model:

                try:
                    answer = self._generate_with_retry(
                        prompt=prompt,
                        model=self.settings.fallback_model,
                    )

                    return (
                        answer,
                        self.settings.fallback_model,
                    )

                except Exception:
                    pass

            raise primary_error

    def _generate_with_retry(
        self,
        prompt: str,
        model: str,
    ) -> str:

        last_error = None

        for attempt in range(
            self.max_retries
        ):

            try:

                response = (
                    self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return response.text.strip()

            except Exception as error:

                last_error = error

                if attempt == self.max_retries - 1:
                    break

                # 1s → 2s → 4s
                delay = 2 ** attempt

                time.sleep(delay)

        raise last_error