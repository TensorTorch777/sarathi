"""Compose the full answer pipeline (local Gemma via Ollama)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.answer import GenerateAnswerUseCase
from app.core.config import Settings
from app.infrastructure.answer.citation_verifier import AnswerCitationVerifier
from app.infrastructure.answer.emotion_detector import LexiconEmotionDetector
from app.infrastructure.answer.generator import OllamaAnswerGenerator, TemplateAnswerGenerator
from app.infrastructure.answer.prompt_builder import GroundedPromptBuilder
from app.infrastructure.answer.query_rewriter import GitaQueryRewriter
from app.infrastructure.answer.topic_detector import LexiconTopicDetector
from app.infrastructure.llm.ollama import OllamaClient
from app.infrastructure.memory.factory import build_recall_memory_use_case
from app.infrastructure.retrieval import build_retrieve_verses_use_case


async def build_generate_answer_use_case(
    *,
    session: AsyncSession,
    settings: Settings,
    use_inmemory_dense: bool = False,
) -> GenerateAnswerUseCase:
    """Wire Emotion → Topic → Rewrite → Hybrid → Memory → Prompt → Gemma → Verify."""
    ollama: OllamaClient | None = None
    if settings.use_local_llm:
        ollama = OllamaClient(settings)

    retrieve = await build_retrieve_verses_use_case(
        session=session,
        settings=settings,
        use_inmemory_dense=use_inmemory_dense,
        ollama=ollama,
    )

    if settings.use_local_llm and ollama is not None:
        generator: OllamaAnswerGenerator | TemplateAnswerGenerator = OllamaAnswerGenerator(
            settings,
            client=ollama,
        )
        llm = ollama
    else:
        generator = TemplateAnswerGenerator()
        llm = None

    recall = None
    if settings.memory_enabled and not use_inmemory_dense:
        recall = build_recall_memory_use_case(session=session, settings=settings)

    return GenerateAnswerUseCase(
        emotion_detector=LexiconEmotionDetector(settings, llm=llm),
        topic_detector=LexiconTopicDetector(settings, llm=llm),
        query_rewriter=GitaQueryRewriter(settings, llm=llm),
        retrieve_verses=retrieve,
        prompt_builder=GroundedPromptBuilder(),
        generator=generator,
        citation_verifier=AnswerCitationVerifier(),
        recall_memory=recall,
        memory_top_k=settings.memory_recall_top_k,
    )
