# Samsung Health + Claude

Programa em Python, gratuito, que lê os dados exportados do Samsung Health e responde
perguntas como:

- Quantos passos eu dei essa semana?
- Qual foi minha última frequência cardíaca?
- Qual foi minha última atividade?
- Quanto eu dormi?

## 1. Exportar os dados no celular

No Samsung Health: **⋮ → Configurações → Baixar dados pessoais**.
Passe a pasta gerada (`Download/Samsung Health/...`) para o computador.

Para atualizar, é só exportar de novo e trocar a pasta.

## 2. Perguntar pelo terminal

Não precisa instalar nada além do Python 3.10+.

```
python saude_cli.py CAMINHO_DA_PASTA passos semana
python saude_cli.py CAMINHO_DA_PASTA passos hoje
python saude_cli.py CAMINHO_DA_PASTA coracao
python saude_cli.py CAMINHO_DA_PASTA atividade
python saude_cli.py CAMINHO_DA_PASTA sono
python saude_cli.py CAMINHO_DA_PASTA resumo
```

Teste com os dados de exemplo: `python saude_cli.py exemplo resumo`

## 3. Perguntar direto para o Claude (app de desktop)

1. `pip install mcp`
2. No Claude Desktop: **Configurações → Desenvolvedor → Editar configuração** e adicione:

```json
{
  "mcpServers": {
    "samsung-health": {
      "command": "python",
      "args": ["C:/caminho/para/1/servidor_mcp.py"],
      "env": { "SAMSUNG_HEALTH_PASTA": "C:/caminho/para/Samsung Health" }
    }
  }
}
```

3. Reinicie o Claude e pergunte: *"Quantos passos eu dei essa semana?"*

Os dados ficam só no seu computador.

## Testes

```
python -m unittest discover -s tests
```
