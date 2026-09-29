from app.core.config import Settings


class RoutingService:

    COMPLEX_KEYWORDS = {
        "compare",
        "analyze",
        "architecture",
        "design",
        "difference",
        "tradeoff",
        "trade-offs",
        "implementation",
        "evaluate",
        "multiple",
    }

    def __init__(self, settings: Settings):
        self.settings = settings

    def classify(
        self,
        query: str,
    ) -> str:

        words = query.lower().split()

        score = 0

        if len(words) > 20:
            score += 1

        if len(words) > 40:
            score += 1

        for word in words:

            clean_word = word.strip(
                ".,?!:"
            )

            if clean_word in self.COMPLEX_KEYWORDS:
                score += 1

        if score >= 2:
            return "large"

        return "small"

    def select_model(
        self,
        query: str,
    ) -> str:

        route = self.classify(query)

        if route == "large":
            return self.settings.large_model

        return self.settings.small_model