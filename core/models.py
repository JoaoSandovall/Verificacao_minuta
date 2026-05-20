from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Tuple, Any

class ErroDetalhe(BaseModel):
    mensagem: str
    original: Optional[str] = None
    sugestao: Optional[str] = None
    span: Optional[Tuple[int, int]] = None
    tipo: Optional[str] = None

class ResultadoRegra(BaseModel):
    status: str = Field(..., description="Pode ser OK, FALHA ou ALERTA")
    detalhe: Union[str, List[Union[str, ErroDetalhe]]] = Field(default_factory=list)

    @field_validator("detalhe", mode="before")
    @classmethod
    def normalizar_detalhe(cls, v: Any) -> Any:
        if isinstance(v, dict):
            return [v]
        return v