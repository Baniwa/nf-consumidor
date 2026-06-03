import pytest
from decimal import Decimal
from dataclasses import FrozenInstanceError
from nf_consumidor.domain.shared.value_objects import CNPJ, ValorMonetario, AliquotaImposto

class TestCNPJ: 
    def test_cnpj_valido_com_mascara(self):
        cnpj = CNPJ("11.222.333/0001-81")
        assert cnpj is not None
    
    def test_cnpj_valido_sem_mascara(self):
        cnpj = CNPJ("11222333000181")
        assert cnpj is not None

    def test_cnpj_normaliza_valor(self):
        cnpj = CNPJ("11.222.333/0001-81")
        assert cnpj.valor == "11222333000181"

    def test_cnpj_formato_str(self):
        cnpj = CNPJ("11222333000181")
        assert str(cnpj) == "11.222.333/0001-81"

    def test_cnpj_digito_invalido(self):
        with pytest.raises(ValueError, match="Dígitos verificadores não conferem"):
            CNPJ("11.222.333/0001-00")
    
    def test_cnpj_sequencia_repetida(self):
        with pytest.raises(ValueError, match="Sequência repetida detectada"):
            CNPJ("00000000000000")
    
    def test_cnpj_tamanho_errado(self):
        with pytest.raises(ValueError, match="Deve conter 14 dígitos"):
            CNPJ("1234")

    def test_cnpj_imutavel(self):
        cnpj = CNPJ("11.222.333/0001-81")
        with pytest.raises(FrozenInstanceError):
            cnpj.valor = "outro"


class TestValorMonetario:
    def test_valor_aceita_decimal(self):
        vm = ValorMonetario(Decimal("10.50"))
        assert vm.valor == Decimal("10.50")

    def test_valor_aceita_int(self):
        vm = ValorMonetario(10)
        assert vm.valor == Decimal("10.00")

    def test_valor_aceita_string(self):
        vm = ValorMonetario("10.50")
        assert vm.valor == Decimal("10.50")

    def test_valor_negativo_rejeitado(self):
        with pytest.raises(ValueError, match="Valor monetário não pode ser negativo"):
            ValorMonetario('-1')

    def test_valor_arrendondamento_half_up(self):
        vm = ValorMonetario("1.005")
        assert vm.valor == Decimal("1.01")

    def test_valor_soma(self):
        v1 = ValorMonetario("10")
        v2 = ValorMonetario("5")
        resultado = v1 + v2
        assert resultado == ValorMonetario("15")

    def test_valor_subtracao(self):
        v1 = ValorMonetario("10")
        v2 = ValorMonetario("3")
        resultado = v1 - v2
        assert resultado == ValorMonetario("7")    

    def test_valor_multiplicacao(self):
        v1 = ValorMonetario("10")
        resultado = v1 * 2
        assert resultado == ValorMonetario("20")    

    def test_valor_str_formato_br(self):
        vm = ValorMonetario("1234.56")
        assert str(vm) == "R$ 1.234,56"


class TestAliquotaImposto:
    def test_aliquota_valida(self):
        aliquota = AliquotaImposto("18")
        assert aliquota.porcentagem == Decimal("18.0000")

    def test_aliquota_zero_valida(self):
        aliquota = AliquotaImposto("0")
        assert aliquota.porcentagem == Decimal("0.0000")

    def test_aliquota_cem_valida(self):
        aliquota = AliquotaImposto("100")
        assert aliquota.porcentagem == Decimal("100.0000")   

    def test_aliquota_negativa_rejeitada(self):
        with pytest.raises(ValueError, match="Aliquota deve estar entre 0% e 100%"):
            AliquotaImposto("-1")            
  
    def test_aliquota_acima_cem_rejeitada(self):
        with pytest.raises(ValueError, match="Aliquota deve estar entre 0% e 100%"):
            AliquotaImposto("100.01")

    def test_aliquota_aplicar_sobre(self):
        aliquota = AliquotaImposto("18")
        base_calculo = ValorMonetario("100")
        imposto_calculado = aliquota.aplicar_sobre(base_calculo)
        assert imposto_calculado == ValorMonetario("18")

    def test_aliquota_srt_formato(self):
        aliquota = AliquotaImposto("18.5")
        assert str(aliquota) == "18,50%"  