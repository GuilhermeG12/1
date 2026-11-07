# Samsung Health → Google Planilhas → Claude

Sem conta nova: usa a sua conta Google.

O celular manda os dados sozinho para uma planilha sua. Quando você quiser,
pergunta para o Claude.

## 1. Criar a planilha (uma vez só)

Dá para fazer no celular, mas é mais fácil no computador. No celular, use o Chrome
com **⋮ → Site para computador** ligado.

1. Abra **sheets.new** (cria uma planilha nova). Dê um nome, ex.: *Saúde*.
2. **Arquivo → Configurações** → Fuso horário: **(GMT-03:00) São Paulo**.
3. **Extensões → Apps Script**.
4. Apague o que tiver lá e cole todo o conteúdo do arquivo `Codigo.gs`.
5. Na linha `const CHAVE = 'TROQUE-ESTA-CHAVE';`, troque por uma senha sua,
   só letras e números (ex.: `a8Kd93mQz`). Salve (ícone de disquete).

## 2. Publicar

1. **Implantar → Nova implantação**.
2. Na engrenagem, escolha **App da Web**.
3. **Executar como:** Eu. **Quem pode acessar:** Qualquer pessoa.
4. **Implantar** → **Autorizar acesso** → escolha sua conta.
   Se aparecer "O Google não verificou este app": **Avançado → Acessar (não seguro)**.
   É normal: o app é seu.
5. Copie o **URL do app da Web** (termina em `/exec`).

## 3. Ligar no HC Webhook

1. Aba **Webhooks → adicionar**.
2. Cole o URL e acrescente no final: `?chave=SUA_SENHA`
   Ex.: `https://script.google.com/macros/s/AKfy.../exec?chave=a8Kd93mQz`
3. Salve e toque em **Sincronizar agora**.
4. Abra a planilha: devem aparecer abas como `steps`, `heart_rate`, `sleep`.

## 4. Perguntar para o Claude

Mande no chat o mesmo link (com `?chave=...`) e pergunte, por exemplo:
*"Leia este link e me diga quantos passos eu dei essa semana."*

Dica: crie um **Projeto** no app do Claude e coloque o link nas instruções do
projeto. Assim não precisa colar toda vez.

## Cuidados

- Quem tiver o link com a chave vê o seu resumo de saúde. Não compartilhe.
- Se a chave vazar, troque no script e faça **Implantar → Gerenciar implantações →
  editar → Nova versão**, e atualize o link no HC Webhook.
- Mudou o código? Sempre publique uma **nova versão**, senão o link continua com
  o código antigo.
