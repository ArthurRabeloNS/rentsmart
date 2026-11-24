"""
RentSmart — Sistema de Orçamento de Locação com Python e Orientação a Objetos
Cliente: R.M Imóveis

Estrutura:
    Imovel (classe abstrata)
     ├── Apartamento
     ├── Casa
     └── Estudio
    Orcamento  -> projeção de 12 meses + exportação para CSV

Pilares de POO aplicados:
    Abstração      -> Imovel define o "contrato" que todo imóvel deve cumprir.
    Encapsulamento -> atributos privados (_quartos, _vagas...) com validação em properties.
    Herança        -> Apartamento, Casa e Estudio herdam de Imovel.
    Polimorfismo   -> calcular_adicionais() e calcular_desconto() têm comportamento
                      diferente em cada subclasse, mas são chamados da mesma forma.

Execução:  python rentsmart.py
"""

import csv
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

# ----------------------------------------------------------------------
# Constantes de negócio e utilitários
# ----------------------------------------------------------------------
TAXA_CONTRATUAL = Decimal("2000.00")   # valor fixo do contrato
MAX_PARCELAS = 5                       # parcelamento de 1x até 5x
MESES_PROJECAO = 12                    # projeção do primeiro ano
ARQUIVO_CSV = "orcamento_rentsmart.csv"
LIMITE_VAGAS_ESTUDIO = 10              # limite de segurança para a validação


def arredondar(valor: Decimal) -> Decimal:
    """Arredonda para 2 casas decimais (centavos), padrão comercial."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def moeda(valor: Decimal) -> str:
    """Formata Decimal no padrão brasileiro: R$ 1.234,56."""
    texto = f"{valor:,.2f}"                       # ex.: 1,234.56
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def decimal_csv(valor: Decimal) -> str:
    """Formata número para o CSV com vírgula decimal (abre direto no Excel pt-BR)."""
    return f"{valor:.2f}".replace(".", ",")


# ----------------------------------------------------------------------
# Hierarquia de imóveis (Abstração, Herança e Polimorfismo)
# ----------------------------------------------------------------------
class Imovel(ABC):
    """Classe base abstrata: define o que todo imóvel precisa saber calcular."""

    def __init__(self, vagas: int):
        self._vagas = 0
        self.vagas = vagas  # passa pela validação do setter

    # --- Encapsulamento: acesso controlado às vagas ---
    @property
    def vagas(self) -> int:
        return self._vagas

    @vagas.setter
    def vagas(self, valor: int) -> None:
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("O número de vagas deve ser um inteiro >= 0.")
        self._validar_vagas(valor)
        self._vagas = valor

    def _validar_vagas(self, valor: int) -> None:
        """Gancho que as subclasses podem sobrescrever para limitar as vagas."""

    # --- Contrato abstrato (cada subclasse é obrigada a implementar) ---
    @property
    @abstractmethod
    def categoria(self) -> str:
        """Nome da categoria exibido no orçamento."""

    @property
    @abstractmethod
    def aluguel_base(self) -> Decimal:
        """Aluguel-base mensal da categoria."""

    @abstractmethod
    def calcular_adicionais(self) -> list:
        """Retorna lista de tuplas (descrição, valor) dos adicionais mensais."""

    # --- Comportamento comum, reaproveitado por todas as subclasses ---
    def total_adicionais(self) -> Decimal:
        return sum((valor for _, valor in self.calcular_adicionais()), Decimal("0.00"))

    def calcular_subtotal(self) -> Decimal:
        """Aluguel-base + adicionais (valor sobre o qual o desconto incide)."""
        return self.aluguel_base + self.total_adicionais()

    def calcular_desconto(self) -> Decimal:
        """Por padrão não há desconto. Apartamento sobrescreve este método."""
        return Decimal("0.00")

    def calcular_aluguel_final(self) -> Decimal:
        """Valor mensal final do aluguel = subtotal - desconto."""
        return arredondar(self.calcular_subtotal() - self.calcular_desconto())


class Apartamento(Imovel):
    """Apartamento: base R$ 700; 2 quartos +R$ 200; garagem +R$ 300; desconto de 5% sem crianças."""

    ALUGUEL_BASE = Decimal("700.00")
    ADICIONAL_2_QUARTOS = Decimal("200.00")
    VALOR_GARAGEM = Decimal("300.00")
    PERCENTUAL_DESCONTO = Decimal("0.05")

    def __init__(self, quartos: int, vagas: int, tem_criancas: bool):
        super().__init__(vagas)
        if quartos not in (1, 2):
            raise ValueError("Apartamento possui 1 ou 2 quartos.")
        self._quartos = quartos
        self._tem_criancas = tem_criancas

    def _validar_vagas(self, valor: int) -> None:
        if valor > 1:
            raise ValueError("Apartamento aceita 0 ou 1 vaga de garagem.")

    @property
    def categoria(self) -> str:
        return f"Apartamento ({self._quartos} quarto{'s' if self._quartos == 2 else ''})"

    @property
    def aluguel_base(self) -> Decimal:
        return self.ALUGUEL_BASE

    @property
    def tem_criancas(self) -> bool:
        return self._tem_criancas

    def calcular_adicionais(self) -> list:
        adicionais = []
        if self._quartos == 2:
            adicionais.append(("Adicional 2º quarto", self.ADICIONAL_2_QUARTOS))
        if self.vagas == 1:
            adicionais.append(("Garagem (1 vaga)", self.VALOR_GARAGEM))
        return adicionais

    def calcular_desconto(self) -> Decimal:
        """Polimorfismo: só o Apartamento tem desconto (5% se NÃO houver crianças)."""
        if not self._tem_criancas:
            return arredondar(self.calcular_subtotal() * self.PERCENTUAL_DESCONTO)
        return Decimal("0.00")


class Casa(Imovel):
    """Casa: base R$ 900; 2 quartos +R$ 250; garagem +R$ 300."""

    ALUGUEL_BASE = Decimal("900.00")
    ADICIONAL_2_QUARTOS = Decimal("250.00")
    VALOR_GARAGEM = Decimal("300.00")

    def __init__(self, quartos: int, vagas: int):
        super().__init__(vagas)
        if quartos not in (1, 2):
            raise ValueError("Casa possui 1 ou 2 quartos.")
        self._quartos = quartos

    def _validar_vagas(self, valor: int) -> None:
        if valor > 1:
            raise ValueError("Casa aceita 0 ou 1 vaga de garagem.")

    @property
    def categoria(self) -> str:
        return f"Casa ({self._quartos} quarto{'s' if self._quartos == 2 else ''})"

    @property
    def aluguel_base(self) -> Decimal:
        return self.ALUGUEL_BASE

    def calcular_adicionais(self) -> list:
        adicionais = []
        if self._quartos == 2:
            adicionais.append(("Adicional 2º quarto", self.ADICIONAL_2_QUARTOS))
        if self.vagas == 1:
            adicionais.append(("Garagem (1 vaga)", self.VALOR_GARAGEM))
        return adicionais


class Estudio(Imovel):
    """Estúdio: base R$ 1.200; pacote de 2 vagas R$ 250; vaga extra (>2) +R$ 60 cada."""

    ALUGUEL_BASE = Decimal("1200.00")
    PACOTE_ESTACIONAMENTO = Decimal("250.00")
    VAGAS_NO_PACOTE = 2
    VALOR_VAGA_EXTRA = Decimal("60.00")

    def __init__(self, vagas: int):
        super().__init__(vagas)

    @property
    def categoria(self) -> str:
        return "Estúdio"

    @property
    def aluguel_base(self) -> Decimal:
        return self.ALUGUEL_BASE

    def calcular_adicionais(self) -> list:
        """0 vagas = sem estacionamento; 1 ou 2 vagas = pacote; acima de 2 = pacote + extras."""
        adicionais = []
        if self.vagas > 0:
            adicionais.append((f"Pacote estacionamento ({self.VAGAS_NO_PACOTE} vagas)",
                               self.PACOTE_ESTACIONAMENTO))
            extras = max(0, self.vagas - self.VAGAS_NO_PACOTE)
            if extras > 0:
                adicionais.append((f"Vagas extras ({extras} x {moeda(self.VALOR_VAGA_EXTRA)})",
                                   self.VALOR_VAGA_EXTRA * extras))
        return adicionais


# ----------------------------------------------------------------------
# Orçamento: projeção de 12 meses e exportação CSV
# ----------------------------------------------------------------------
class Orcamento:
    """Une um imóvel à taxa contratual parcelada e gera a projeção anual."""

    def __init__(self, imovel: Imovel, parcelas_taxa: int):
        if not 1 <= parcelas_taxa <= MAX_PARCELAS:
            raise ValueError(f"O parcelamento deve ser de 1x a {MAX_PARCELAS}x.")
        self._imovel = imovel
        self._parcelas_taxa = parcelas_taxa

    @property
    def imovel(self) -> Imovel:
        return self._imovel

    @property
    def parcelas_taxa(self) -> int:
        return self._parcelas_taxa

    def calcular_parcelas_taxa(self) -> list:
        """Divide a taxa em N parcelas; a última absorve a diferença de centavos."""
        valor_parcela = arredondar(TAXA_CONTRATUAL / self._parcelas_taxa)
        parcelas = [valor_parcela] * (self._parcelas_taxa - 1)
        parcelas.append(TAXA_CONTRATUAL - valor_parcela * (self._parcelas_taxa - 1))
        return parcelas

    def projetar_12_meses(self) -> list:
        """Retorna lista de dicionários com Mês, Aluguel, Parcela e Total de cada mês."""
        aluguel = self._imovel.calcular_aluguel_final()
        parcelas = self.calcular_parcelas_taxa()
        projecao = []
        for mes in range(1, MESES_PROJECAO + 1):
            parcela = parcelas[mes - 1] if mes <= len(parcelas) else Decimal("0.00")
            projecao.append({
                "mes": mes,
                "aluguel": aluguel,
                "parcela": parcela,
                "total": aluguel + parcela,
            })
        return projecao

    def exibir_resumo(self) -> None:
        """Mostra o orçamento detalhado no terminal."""
        imovel = self._imovel
        parcelas = self.calcular_parcelas_taxa()
        linha = "=" * 62

        print(f"\n{linha}\n{'ORÇAMENTO RENTSMART - R.M IMÓVEIS':^62}\n{linha}")
        print(f"Imóvel: {imovel.categoria}")
        print("-" * 62)
        print(f"{'Aluguel-base':<42}{moeda(imovel.aluguel_base):>20}")

        adicionais = imovel.calcular_adicionais()
        if adicionais:
            for descricao, valor in adicionais:
                print(f"  + {descricao:<38}{moeda(valor):>20}")
        else:
            print(f"{'Adicionais':<42}{moeda(Decimal('0.00')):>20}")

        print(f"{'Subtotal (base + adicionais)':<42}{moeda(imovel.calcular_subtotal()):>20}")

        desconto = imovel.calcular_desconto()
        if desconto > 0:
            print(f"  - {'Desconto de 5% (sem crianças)':<38}{moeda(desconto):>20}")

        print("-" * 62)
        print(f"{'VALOR MENSAL FINAL DO ALUGUEL':<42}{moeda(imovel.calcular_aluguel_final()):>20}")
        print("-" * 62)
        print(f"{'Taxa contratual':<42}{moeda(TAXA_CONTRATUAL):>20}")
        print(f"Parcelamento: {self._parcelas_taxa}x", end="")
        if len(set(parcelas)) == 1:
            print(f" de {moeda(parcelas[0])}")
        else:
            print(f" de {moeda(parcelas[0])} (última de {moeda(parcelas[-1])})")
        print("(a taxa é cobrada separadamente do aluguel mensal)")
        print(linha)

    def exportar_csv(self, caminho: str = ARQUIVO_CSV) -> str:
        """Exporta a projeção de 12 meses usando o módulo nativo csv."""
        projecao = self.projetar_12_meses()
        total_aluguel = sum((m["aluguel"] for m in projecao), Decimal("0.00"))
        total_parcelas = sum((m["parcela"] for m in projecao), Decimal("0.00"))
        total_geral = sum((m["total"] for m in projecao), Decimal("0.00"))

        # utf-8-sig + ';' para abrir corretamente no Excel em português
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["Mês", "Aluguel Mensal", "Parcela do Contrato", "Total a Pagar no Mês"])
            for m in projecao:
                escritor.writerow([m["mes"], decimal_csv(m["aluguel"]),
                                   decimal_csv(m["parcela"]), decimal_csv(m["total"])])
            escritor.writerow(["TOTAL 12 MESES", decimal_csv(total_aluguel),
                               decimal_csv(total_parcelas), decimal_csv(total_geral)])
        return caminho


# ----------------------------------------------------------------------
# Entrada de dados com validação rigorosa (loops while)
# ----------------------------------------------------------------------
def ler_opcao(mensagem: str, validas: tuple) -> str:
    """Repete a pergunta até o usuário digitar uma das opções válidas."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in validas:
            return resposta
        print(f"  ⚠ Opção inválida! Escolha entre: {', '.join(validas)}.")


def ler_inteiro(mensagem: str, minimo: int, maximo: int) -> int:
    """Repete a pergunta até o usuário digitar um inteiro dentro do intervalo."""
    while True:
        resposta = input(mensagem).strip()
        if resposta.isdigit() and minimo <= int(resposta) <= maximo:
            return int(resposta)
        print(f"  ⚠ Valor inválido! Digite um número inteiro de {minimo} a {maximo}.")


def ler_sim_nao(mensagem: str) -> bool:
    """Retorna True para 's' e False para 'n', repetindo até a entrada ser válida."""
    return ler_opcao(mensagem, ("s", "n")) == "s"


def montar_imovel() -> Imovel:
    """Pergunta os dados ao usuário e devolve o objeto da subclasse correta."""
    print("\nCategorias disponíveis:")
    print("  1 - Apartamento (1 quarto)  - base R$ 700,00")
    print("  2 - Casa (1 quarto)         - base R$ 900,00")
    print("  3 - Estúdio                 - base R$ 1.200,00")
    categoria = ler_opcao("Escolha a categoria (1, 2 ou 3): ", ("1", "2", "3"))

    if categoria == "1":
        quartos = ler_inteiro("Quantos quartos? (1 ou 2): ", 1, 2)
        vagas = ler_inteiro("Vagas de garagem (0 ou 1): ", 0, 1)
        tem_criancas = ler_sim_nao("Possui crianças? (s/n): ")
        return Apartamento(quartos, vagas, tem_criancas)

    if categoria == "2":
        quartos = ler_inteiro("Quantos quartos? (1 ou 2): ", 1, 2)
        vagas = ler_inteiro("Vagas de garagem (0 ou 1): ", 0, 1)
        return Casa(quartos, vagas)

    vagas = ler_inteiro(f"Vagas de estacionamento (0 a {LIMITE_VAGAS_ESTUDIO}; "
                        f"pacote inicial de 2 vagas): ", 0, LIMITE_VAGAS_ESTUDIO)
    return Estudio(vagas)


def main() -> None:
    print("=" * 62)
    print(f"{'RENTSMART - Orçamento de Locação | R.M Imóveis':^62}")
    print("=" * 62)

    while True:
        imovel = montar_imovel()
        print(f"\nA taxa contratual é de {moeda(TAXA_CONTRATUAL)} "
              f"e pode ser parcelada de 1x a {MAX_PARCELAS}x.")
        parcelas = ler_inteiro(f"Em quantas parcelas deseja pagar a taxa? (1 a {MAX_PARCELAS}): ",
                               1, MAX_PARCELAS)

        orcamento = Orcamento(imovel, parcelas)
        orcamento.exibir_resumo()
        arquivo = orcamento.exportar_csv()
        print(f"\n✔ Projeção dos 12 meses salva em '{arquivo}'.")

        if not ler_sim_nao("\nDeseja gerar outro orçamento? (s/n): "):
            break

    print("\nObrigado por utilizar o RentSmart!")


if __name__ == "__main__":
    main()
