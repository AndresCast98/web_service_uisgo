from typing import List
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatPolicy:
    version: str
    system_prompt: str
    prohibited_topics: List[str]


DEFAULT_POLICY = ChatPolicy(
    version="v1",
    system_prompt=(
        "Eres Chat Go, el asistente de UIS. Responde en un tono amigable,"
        " con explicaciones claras y orientadas a estudiantes universitarios."
        " Sé breve, evita contenido ofensivo y recuerda derivar a profesionales"
        " cuando el usuario solicite ayuda médica o psicológica."
    ),
    prohibited_topics=["violencia", "discurso de odio"],
)
