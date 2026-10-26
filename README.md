# odonto em 5.

Newsletter semanal para graduandos de Odontologia, com carrossel no Instagram. Este repositório guarda as edições aprovadas e publica tudo automaticamente.

## Como funciona

1. **De segunda a sexta**, os agentes do Claude coletam pautas todo dia.
2. **No sábado**, eles montam a edição com `"aprovado": false` e mandam a prévia: e-mail, carrossel, legenda e comentário-enquete.
3. **No fim de semana**, você revisa e responde "aprovado". Só edição aprovada é publicada.
4. **No sábado às 6h13**, a rotina conta os votos da enquete da semana anterior, antes da montagem da edição.
5. **Na segunda, entre 6h03 e 6h30**, a rotina envia a newsletter pela Brevo. **Por volta das 12h**, publica o carrossel-resumo no Instagram, com o comentário-enquete.

Nada é publicado enquanto a variável `MODO_TESTE` estiver como `sim`, nem enquanto a edição estiver com `"aprovado": false`. O manual dos agentes está em [AGENTES.md](AGENTES.md).

## Posts avulsos (estilo the news)

Além da edição de segunda, o Instagram recebe **3 posts avulsos por semana**: uma imagem com a manchete e a matéria completa na legenda, sempre com a fonte.

- **Quando:** terça, quarta e sexta, às 12h07. A rotina publica os posts cuja data `publicar_em` é o dia.
- **Trava de revisão:** só sai post com `"revisado": true`. Quem marca isso é o revisor, depois de conferir o texto com a fonte.
- **Notícia urgente:** o calendário é o mínimo, não o máximo. Um post com `"urgente": true` e `"revisado": true` é publicado assim que entra na branch `main`, sem esperar o dia agendado. Os agentes marcam como urgente: oportunidade com prazo em até 7 dias, decisão do CFO, da Anvisa ou da Justiça que afete estudantes ou dentistas, e notícia de grande repercussão na área. Limite de 1 post urgente por dia.
- **Publicar na hora:** um post com `"publicar_agora": true` e `"revisado": true` sai assim que entra na branch `main`. É assim que o Claude publica quando você pede.
- **Carrossel:** coloque `"carrossel": ["01.jpg", "02.jpg", ...]` no post.json (de 2 a 20 imagens JPEG, 1080x1350). Sem isso, o post usa `post.jpg`.
- **Publicação manual:** **Actions → Publicar posts avulsos → Run workflow**, com o nome da pasta do post em `post_id`.
- **Aprovação:** os posts da semana seguinte chegam na sexta, junto com a prévia da edição; notícia urgente chega quando aparece.

Estrutura de um post:

```
posts/AAAA-MM-DD-assunto/
  post.json   tipo, publicar_em, revisado, rotulo, manchete, destaque, legenda, comentario (opcional)
  arte.jpg    gráfico ou ilustração própria
  post.jpg    imagem final, gerada com: python ferramentas/gerar_post.py posts/AAAA-MM-DD-assunto
```

Tipos de post que se alternam: notícia, estudo explicado, oportunidade com prazo e "Você sabia?".

**Regra:** post avulso traz assunto novo da semana. Nunca repete o que já saiu na newsletter de segunda e nunca usa as pautas mais fortes, que ficam guardadas para a edição da segunda seguinte: a newsletter tem que ser sempre o conteúdo mais chamativo. Os posts usam pautas boas de segundo nível, oportunidades com prazo que vence antes da próxima segunda e "Você sabia?".

## Estrutura de uma edição

```
edicoes/AAAA-MM-DD/
  edicao.json        legenda, comentário-enquete, assunto do e-mail, resposta da enquete
  email.html         newsletter ({{BASE}} vira o endereço público das imagens)
  slides/01.jpg ...  carrossel, 1080x1350, JPEG
  imagens/           imagens do e-mail
```

Depois da publicação, a rotina grava `publicado_instagram.json`, `enviado_email.json` e `resultado_enquete.json` na pasta da edição.

## Configuração (uma vez só)

Em **Settings → Secrets and variables → Actions**:

**Secrets** (ficam escondidos; nem os agentes veem):

| Nome | O que é |
| --- | --- |
| `IG_USER_ID` | ID da conta profissional do Instagram |
| `IG_ACCESS_TOKEN` | Token de longa duração do app da Meta (Instagram Login) |
| `BREVO_API_KEY` | Chave de API da Brevo |
| `BREVO_LISTA_ID` | Número da lista de inscritos na Brevo |
| `BREVO_REMETENTE_EMAIL` | E-mail remetente já verificado na Brevo |
| `GH_PAT` | Token do GitHub com permissão de editar segredos (só para a renovação automática do token do Instagram) |

**Variables**:

| Nome | Valor |
| --- | --- |
| `MODO_TESTE` | `sim` até o primeiro teste dar certo; depois `não` |
| `PUBLICAR_INSTAGRAM` | Só publica no Instagram se for `sim`. Sem a variável, ou com `não`, o Instagram fica desligado |
| `BREVO_REMETENTE_NOME` | `odonto em 5` |
| `BREVO_EMAIL_TESTE` | Opcional: um ou mais e-mails separados por vírgula. Com ela preenchida, a newsletter vai só para esses e-mails |

## Testar

**Actions → Publicar edição → Run workflow**, com a data da edição e `modo_teste = sim`. O registro mostra as imagens, a legenda e o comentário que seriam publicados, sem publicar nada.

## Limitações conhecidas

- O Instagram não oferece enquete nativa pela API. A enquete é um comentário com alternativas A a D, e os votos são contados pelas respostas.
- O comentário não pode ser fixado pela API; fixe-o pelo aplicativo, se quiser.
- Links na legenda do Instagram não são clicáveis; por isso as referências vão como citação com DOI.
- **Novos inscritos no meio da semana:** a rotina "Enviar edição para novos inscritos" roda de hora em hora e manda a edição da semana para quem se inscreveu depois do envio de segunda (com um aviso no topo). Precisa que a chave da Brevo tenha permissão completa de contatos. Para desligar, crie a variável `ENVIAR_ATRASADOS = não`.
- O token do Instagram vale 60 dias. A rotina `Renovar token` renova nos dias 1 e 15; sem `GH_PAT`, ela avisa, mas não consegue salvar o token novo.
- No plano gratuito da Brevo, o limite é de 300 e-mails por dia.
