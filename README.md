# odonto em 5.

Newsletter semanal para graduandos de Odontologia, com carrossel no Instagram. Este repositório guarda as edições aprovadas e publica tudo automaticamente.

## Como funciona

1. **De segunda a quinta**, os agentes do Claude coletam pautas todo dia.
2. **Na sexta**, eles montam a edição e abrem uma *pull request* com ela: slides, legenda, comentário-enquete e e-mail.
3. **No fim de semana**, você revisa a pull request e aprova com **Merge**. Só o que está na branch `main` é publicado.
4. **No domingo ao meio-dia**, a rotina conta os votos da enquete da semana anterior.
5. **Na segunda às 7h**, a rotina publica o carrossel com legenda, posta o comentário-enquete e envia a newsletter pela Brevo.

Nada é publicado enquanto a variável `MODO_TESTE` estiver como `sim`.

## Posts avulsos (estilo the news)

Além da edição de segunda, o Instagram recebe **3 posts avulsos por semana**: uma imagem com a manchete e a matéria completa na legenda, sempre com a fonte.

- **Quando:** terça, quarta e sexta, às 12h07. A rotina publica os posts cuja data `publicar_em` é o dia.
- **Trava de revisão:** só sai post com `"revisado": true`. Quem marca isso é o revisor, depois de conferir o texto com a fonte.
- **Notícia urgente:** o calendário é o mínimo, não o máximo. Um post com `"urgente": true` e `"revisado": true` é publicado assim que entra na branch `main`, sem esperar o dia agendado. Os agentes marcam como urgente: oportunidade com prazo em até 7 dias, decisão do CFO, da Anvisa ou da Justiça que afete estudantes ou dentistas, e notícia de grande repercussão na área. Limite de 1 post urgente por dia.
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
| `PUBLICAR_INSTAGRAM` | `não` para enviar só a newsletter (fase de lançamento); `sim` quando o Instagram entrar |
| `BREVO_REMETENTE_NOME` | `odonto em 5` |
| `BREVO_EMAIL_TESTE` | Opcional: seu e-mail. Com ele preenchido, a newsletter vai só para você |

## Testar

**Actions → Publicar edição → Run workflow**, com a data da edição e `modo_teste = sim`. O registro mostra as imagens, a legenda e o comentário que seriam publicados, sem publicar nada.

## Limitações conhecidas

- O Instagram não oferece enquete nativa pela API. A enquete é um comentário com alternativas A a D, e os votos são contados pelas respostas.
- O comentário não pode ser fixado pela API; fixe-o pelo aplicativo, se quiser.
- Links na legenda do Instagram não são clicáveis; por isso as referências vão como citação com DOI.
- O token do Instagram vale 60 dias. A rotina `Renovar token` renova nos dias 1 e 15; sem `GH_PAT`, ela avisa, mas não consegue salvar o token novo.
- No plano gratuito da Brevo, o limite é de 300 e-mails por dia.
