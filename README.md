# 🏠 RentSmart — Sistema de Orçamento de Locação

Sistema em **Python** com **Programação Orientada a Objetos** que gera orçamentos de locação para a imobiliária **R.M Imóveis**. A partir das escolhas do cliente, o programa calcula o aluguel mensal, aplica adicionais e descontos, parcela a taxa contratual e exporta a projeção dos 12 primeiros meses em um arquivo **CSV**.

## ✨ Funcionalidades

- Três categorias de imóvel: **Apartamento**, **Casa** e **Estúdio**
- Cálculo de adicionais (2º quarto, garagem, estacionamento e vagas extras)
- Desconto de 5% exclusivo para apartamentos de clientes **sem crianças**
- Taxa contratual de R$ 2.000,00 parcelável de **1x a 5x**
- Validação rigorosa das entradas (loops `while`)
- Exportação de `orcamento_rentsmart.csv` com a projeção dos 12 meses

## 📋 Regras de negócio

| Categoria | Aluguel-base | 2 quartos | Garagem / Estacionamento |
|---|---|---|---|
| Apartamento (1 quarto) | R$ 700,00 | + R$ 200,00 | + R$ 300,00 (0 ou 1 vaga) |
| Casa (1 quarto) | R$ 900,00 | + R$ 250,00 | + R$ 300,00 (0 ou 1 vaga) |
| Estúdio | R$ 1.200,00 | — | Pacote de 2 vagas: R$ 250,00; vaga extra: + R$ 60,00 |

- **Taxa contratual:** R$ 2.000,00, parcelável em 1x a 5x. É exibida separadamente do aluguel e somada apenas nos meses das parcelas na projeção anual.
- **Desconto:** apenas Apartamento sem crianças → 5% sobre o aluguel já com adicionais.

> **Premissa adotada no Estúdio:** o pacote de R$ 250,00 cobre até 2 vagas. Quem escolhe 1 ou 2 vagas paga o pacote; a partir da 3ª vaga soma-se R$ 60,00 por vaga extra; com 0 vagas não há cobrança.

## 🧱 Arquitetura

```
Imovel (classe abstrata)
 ├── Apartamento
 ├── Casa
 └── Estudio

Orcamento  →  projetar_12_meses() · exibir_resumo() · exportar_csv()
```

- **Abstração:** `Imovel` define o contrato (`categoria`, `aluguel_base`, `calcular_adicionais`).
- **Encapsulamento:** atributos privados com validação via `property`.
- **Herança:** as três categorias reaproveitam a lógica de `Imovel`.
- **Polimorfismo:** `calcular_adicionais()` e `calcular_desconto()` se comportam de forma diferente em cada subclasse.

## ▶️ Como executar

**Pré-requisito:** Python 3.8 ou superior. Não é preciso instalar bibliotecas (usa apenas `csv`, `decimal` e `abc` da biblioteca padrão).

```bash
git clone https://github.com/ArthurRabeloNS/rentsmart.git
cd rentsmart
python rentsmart.py
```

No Windows, se `python` não funcionar, use `py rentsmart.py`.

## 💻 Exemplo de execução

```
Escolha a categoria (1, 2 ou 3): 1
Quantos quartos? (1 ou 2): 2
Vagas de garagem (0 ou 1): 1
Possui crianças? (s/n): n
Em quantas parcelas deseja pagar a taxa? (1 a 5): 5

Imóvel: Apartamento (2 quartos)
Aluguel-base                                         R$ 700,00
  + Adicional 2º quarto                              R$ 200,00
  + Garagem (1 vaga)                                 R$ 300,00
Subtotal (base + adicionais)                       R$ 1.200,00
  - Desconto de 5% (sem crianças)                     R$ 60,00
VALOR MENSAL FINAL DO ALUGUEL                      R$ 1.140,00
Taxa contratual                                    R$ 2.000,00
Parcelamento: 5x de R$ 400,00
```

## 📄 Arquivo CSV gerado

`orcamento_rentsmart.csv` (separador `;`, decimal com vírgula, codificação UTF-8 com BOM — abre direto no Excel em português):

| Mês | Aluguel Mensal | Parcela do Contrato | Total a Pagar no Mês |
|---|---|---|---|
| 1 a 5 | 1140,00 | 400,00 | 1540,00 |
| 6 a 12 | 1140,00 | 0,00 | 1140,00 |
| **TOTAL 12 MESES** | 13680,00 | 2000,00 | 15680,00 |

## 🗂️ Estrutura do repositório

```
rentsmart/
├── rentsmart.py
├── README.md
└── orcamento_rentsmart.csv   (gerado na execução)
```

## 👨‍💻 Autor

**Arthur Rabelo Nunes da Silva** — [@ArthurRabeloNS](https://github.com/ArthurRabeloNS)
Projeto acadêmico — Ciência da Computação.
