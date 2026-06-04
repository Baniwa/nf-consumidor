import re 
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Union


@dataclass(frozen=True)
class CNPJ: 
    valor: str

    def __post_init__(self):
        numeros = re.sub(r'\D', '', self.valor)
        if len(numeros) != 14:
            raise ValueError(f"CNPJ inválido: Deve conter 14 dígitos. Recebido o nº{self.valor}")
        if len(set(numeros)) == 1:
            raise ValueError(f"CNPJ inválido: Sequência repetida detectada. Recebido o nº{self.valor}")
        if not self._validar_digitos(numeros):
            raise ValueError(f"CNPJ inválido: Dígitos verificadores não conferem. Recebido o nº{self.valor}")
        
        object.__setattr__(self, 'valor', numeros)
    
    
    @staticmethod
    def _calcular_digito(cnpj_parcial: str, pesos: list[int]) -> int:
        soma = sum(int(digito) * peso for digito, peso in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    def _validar_digitos(self, cnpj_limpo: str) -> bool:
        pesos_primeiro = [5,4,3,2,9,8,7,6,5,4,3,2]
        pesos_segundo = [6,5,4,3,2,9,8,7,6,5,4,3,2]

        primeiro_digito = self._calcular_digito(cnpj_limpo[:12], pesos_primeiro)
        if int(cnpj_limpo[12]) != primeiro_digito:
            return False
        
        segundo_digito = self._calcular_digito(cnpj_limpo[:13], pesos_segundo)
        if int(cnpj_limpo[13]) != segundo_digito:
            return False
        
        return True
    
    def __str__(self) -> str:
        v = self.valor
        return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"

@dataclass(frozen=True)
class ValorMonetario: 
    valor: Decimal

    def __post_init__(self):
        if not isinstance(self.valor, Decimal):
            try:
                object.__setattr__(self, 'valor', Decimal(str(self.valor)))
            except (InvalidOperation, TypeError):
                raise ValueError(f"Valor monetário inválido.")
    
        if self.valor < Decimal('0.00'):
            raise ValueError (f"Valor monetário não pode ser negativo.") 
        
        valor_arredondado = self.valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        object.__setattr__(self, 'valor', valor_arredondado)

# --- Operadores Aritméticos Obrigatórios ---
    def __add__(self, outro: 'ValorMonetario') -> 'ValorMonetario':
        if not isinstance(outro, ValorMonetario):
            return NotImplemented
        return ValorMonetario(self.valor + outro.valor)
    
    def __sub__(self, outro: 'ValorMonetario') -> 'ValorMonetario':
        if not isinstance(outro, ValorMonetario):
            return NotImplemented
        return ValorMonetario(self.valor - outro.valor)
    
    def __mul__(self, fator: Union[Decimal, int, float]) -> 'ValorMonetario':
        try:
            fator_decimal = Decimal(str(fator))
        except (InvalidOperation, TypeError):
            return NotImplemented
        return ValorMonetario(self.valor * fator_decimal)

    def __rmul__(self, fator: Union[Decimal, int, float]) -> 'ValorMonetario':
        return self.__mul__(fator)

    def __str__(self) -> str:
            return f"R$ {self.valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    
@dataclass(frozen=True)
class AliquotaImposto:
    porcentagem: Decimal

    def __post_init__(self):
        if not isinstance(self.porcentagem, Decimal):
            try:
                object.__setattr__(self, 'porcentagem', Decimal(str(self.porcentagem)))
            except (InvalidOperation, TypeError):
                raise ValueError(f"Alíquota inválida.")
            
        if self.porcentagem < Decimal('0.0000') or self.porcentagem > Decimal ('100.0000'):
            raise ValueError(f"Aliquota deve estar entre 0% e 100%")
        aliquota_arredondada = self.porcentagem.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        object.__setattr__(self, 'porcentagem', aliquota_arredondada)

    @property #módulo 
    def fator_multiplicador(self) -> Decimal:
        return self.porcentagem / Decimal('100.0000')
 
    def aplicar_sobre(self, valor: ValorMonetario) -> ValorMonetario:
        if not isinstance(valor, ValorMonetario):
            raise ValueError("O alvo da aplicação da alíquota deve ser uma instância de Valor Monetario.")
        
        resultado_imposto = valor.valor * self.fator_multiplicador
        return ValorMonetario(resultado_imposto)

    def __str__(self) -> str:
        string_formatada = f"{self.porcentagem:.4f}".rstrip('0').rstrip('.')
        if '.' in string_formatada:
            partes = string_formatada.split('.')
            if len(partes[1]) < 2:
                string_formatada = f"{partes[0]}.{partes[1]:0<2}"
        else:
            string_formatada += ".00"
            
        return f"{string_formatada.replace('.', ',')}%"