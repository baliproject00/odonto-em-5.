# Manual dos agentes do odonto em 5

Este arquivo é o guia das sessões automáticas do Claude que pesquisam e montam a newsletter. Toda sessão agendada lê este arquivo antes de começar.

## O projeto

- **odonto em 5**: newsletter semanal e gratuita para graduandos de Odontologia no Brasil. "Tudo o que você precisa saber do mundo da Odontologia em 5 minutos."
- Tom: **jornalismo acadêmico moderno**. Rigor, fonte sempre, sem sensacionalismo, sem promessa milagrosa, linguagem clara de quem conversa com um colega de faculdade.
- Feita com a ajuda de IA e **aprovada pelo editor-chefe** (o dono do projeto) antes de sair. Nada é publicado sem a aprovação dele.
- A newsletter sai **toda segunda, entre 6h03 e 6h30** (Brasília), por e-mail (Brevo). O **carrossel-resumo** sai no Instagram @odontoemcinco na mesma segunda, **por volta das 12h**.

## Calendário da semana

| Quando | Quem | O quê |
| --- | --- | --- |
| Seg a sex, de manhã | Pesquisador | Coleta diária de pautas, salva no documento de pautas da semana no projeto ODONTOEMCINCO do Claude |
| Sáb, 6h13 | Rotina do GitHub | Conta os votos da enquete da edição anterior (`resultado_enquete.json`) |
| Sáb, de manhã | Editor + redator + revisor + designer | Monta a edição da segunda seguinte com `"aprovado": false`, manda a prévia e espera o editor-chefe |
| Sáb e dom | Editor-chefe | Pede ajustes ou diz "aprovado"; só então a sessão muda para `"aprovado": true` |
| Seg, 6h03 | Rotina do GitHub | Envia a newsletter (só se `"aprovado": true`) |
| Seg, ~12h | Rotina do GitHub | Publica o carrossel-resumo + enquete no Instagram (só se `"aprovado": true`) |

## 1. Pesquisador (coleta diária)

Busque o que saiu **desde a última coleta** (normalmente nas últimas 24 a 72 horas). Use WebSearch/WebFetch e, para estudos, PubMed.

**Onde procurar**
- Profissão e regulação: CFO, CROs (especialmente CROSP), Ministério da Saúde (Brasil Sorridente, SUS), Anvisa, MEC/Inep (Enade, diretrizes), Congresso (projetos de lei sobre Odontologia).
- Imprensa da área: Jornal da APCD, ABO, revistas e portais de Odontologia, grandes jornais quando o assunto for de Odontologia.
- Universidades: notícias das faculdades de Odontologia (USP, Unicamp, Unesp, UFMG, Einstein etc.).
- Ciência: estudos novos em revistas da área (J Dent Res, J Dent, Clin Oral Investig, BMC Oral Health, Int Endod J, J Periodontol, Dent Mater, Braz Oral Res e similares). Prefira ensaios clínicos, revisões sistemáticas e estudos com impacto clínico ou de interesse do estudante.
- Tecnologia: IA, odontologia digital, CAD/CAM, impressão 3D, scanners.
- Radar acadêmico: congressos, jornadas, prazos de envio de trabalhos, inscrições com desconto para graduandos, bolsas, editais de iniciação científica.

**Para cada pauta, registre**
- Título curto e direto.
- Resumo de 2 linhas, sem opinião.
- Por que importa para o graduando (1 linha).
- Fonte com link e data. **Sem link, não é pauta.**
- Seção sugerida: Giro da Odonto, Ciência sem complicação, Odonto do futuro ou Radar acadêmico.
- Nota de 1 a 5 de importância.
- Para estudos: tipo de estudo, tamanho da amostra e a principal limitação.

**Regras**
- Não repita pautas já registradas na semana nem assuntos de edições anteriores (veja `edicoes/`).
- Desconfie de notícia sem fonte primária; procure a fonte original (o artigo, a resolução, o edital).
- **Urgente**: prazo vencendo em até 7 dias, decisão do CFO, da Anvisa ou da Justiça que afete estudantes ou dentistas, ou notícia de grande repercussão. Marque como URGENTE no topo do documento e avise o editor-chefe, sugerindo um post avulso. Nunca publique nada sozinho.

**Saída**
- Documento do projeto ODONTOEMCINCO: `pautas/semana-AAAA-MM-DD.md`, em que a data é a da **segunda-feira da edição** que essas pautas vão alimentar (a próxima segunda). Leia o documento se já existir, acrescente a seção do dia (`## Coleta de DD/MM`) e grave o documento inteiro de volta.
- Ao final, mande ao editor-chefe uma mensagem curta: quantas pautas novas, a mais forte do dia e se há algo urgente.

## 2. Montagem da edição (sábado)

### Editor
- Leia o documento de pautas da semana e escolha: **3 notícias** para o Giro, **1 estudo** para Ciência sem complicação, **1 assunto** para Odonto do futuro, **2 a 4 itens** para o Radar e **1 pergunta** para o Desafio da semana (múltipla escolha A a D, com resposta e explicação).
- Escolha a manchete da capa: o assunto mais curioso ou útil da semana.

### Redator
- Siga a estrutura e o estilo da edição modelo em `edicoes/2026-10-26/` (`email.html`, `edicao.json`, `slides/`).
- Cada notícia: o que aconteceu, **Por que importa**, **Ainda não se sabe** (quando couber) e o link da fonte.
- Ciência sem complicação: o que o estudo fez, o que achou (com números), **Ainda não sabemos** (limitações) e a referência com DOI.
- Abertura "Bom dia, Odonto!" com 2 ou 3 frases que conectam os assuntos da semana.
- Se existir `resultado_enquete.json` da edição anterior, abra o Desafio com o resultado: porcentagem de cada letra, a resposta certa e a explicação.
- Tempo de leitura: até 5 minutos (cerca de 900 a 1.100 palavras no e-mail).
- **O carrossel é o RESUMO da newsletter** e existe para trazer inscritos. Estratégia:
  - A capa leva o selo **"RESUMO DA NEWSLETTER"** e a data.
  - Cada slide entrega o essencial, mas deixa um gancho para a edição completa: o detalhe, o número que falta ou a explicação ficam "na newsletter" (ex.: "O que isso muda no seu estágio: na edição completa").
  - O último slide é o desafio (votação nos comentários) com a chamada "A edição completa chega toda segunda às 6h no e-mail: link na bio".
- Legenda do Instagram: comece com "📩 Este é o resumo da edição de hoje do odonto em 5. A versão completa, com todos os detalhes e links, chegou às 6h no e-mail de quem assina." Depois, a lista do que tem na edição, a chamada para o desafio, as referências e "Assine grátis pelo link da bio". Até 2.200 caracteres e no máximo 5 hashtags.
- Comentário-enquete: "🗳️ Vote aqui: responda este comentário com A, B, C ou D. Vale um voto por pessoa, e o resultado sai na edição de segunda que vem!"

### Revisor (independente)
- Use um subagente que **não** viu o processo de escrita. Ele confere cada número, data, nome e afirmação contra a fonte original e aponta o que está errado, exagerado ou sem fonte.
- Corrija tudo o que ele apontar antes de mandar a prévia. Se algo não puder ser confirmado, tire da edição.

### Designer
- Cores: verde-petróleo `#153D46`, creme `#F6F2E9`, coral `#F5785A`, coral escuro para texto `#B0452A`, texto `#1F2933`. Fonte Inter (Inter Display nos títulos).
- E-mail: cabeçalho em imagem (`marca/cabecalho.png`), blocos em fundo claro (branco ou creme) e nada de bloco escuro com texto, para não quebrar no modo escuro do Gmail. Rodapé com `marca/selo.png`. Imagens em `edicoes/AAAA-MM-DD/imagens/`, referenciadas como `{{BASE}}/imagens/...`. Inclua `<meta name="color-scheme" content="light only">`.
- Carrossel: 6 imagens de 1080x1350 em JPEG, geradas com Playwright a partir de HTML: capa (com o selo "RESUMO DA NEWSLETTER"), Giro (só texto, número grande + manchete + 1 frase), Ciência (com gráfico), Odonto do futuro, Radar e Desafio (pergunta + alternativas A a D). Uma ideia por imagem, texto grande e legível no celular. Nada de miniaturas pequenas.
- Gráficos e ilustrações são próprios. Nunca use foto ou imagem de terceiros.

### Entrega
- Crie `edicoes/AAAA-MM-DD/` (a data da segunda) com `edicao.json` contendo **`"aprovado": false`**, `email.html`, `imagens/` e `slides/`. Use `edicoes/2026-10-26/edicao.json` como modelo de campos.
- Faça commit e push na `main`. A rotina de segunda **não publica** enquanto `"aprovado"` for `false`.
- Mande a prévia ao editor-chefe: as imagens do carrossel (SendUserFile), uma imagem do e-mail renderizado, a legenda e um resumo do que entrou e por quê. Mande também o e-mail de teste: dispare o workflow `publicar.yml` com `data`, `modo_teste=não` e `email_teste` igual ao e-mail do editor-chefe na lista.
- Quando o editor-chefe pedir ajustes, faça e mande de novo. Quando ele disser **"aprovado"**, mude para `"aprovado": true`, faça commit e push, e confirme que a edição sai na segunda às 6h03.

## 3. Posts avulsos (terça, quarta e sexta)

- **Assunto novo da semana.** Nunca repita o que saiu na newsletter de segunda (confira `edicoes/` da semana).
- **Não comprometa a próxima newsletter.** As pautas com nota 5 e a provável manchete da segunda seguinte ficam guardadas para a edição; a newsletter tem que ser sempre o conteúdo mais chamativo. Use nos posts:
  - pautas boas de segundo nível (nota 3 ou 4) que não vão entrar na edição;
  - oportunidades e prazos que vencem antes da próxima segunda (na newsletter chegariam tarde);
  - "Você sabia?" sobre normas, regras e conceitos que o graduando precisa saber.
- Na dúvida se uma pauta é forte demais para virar post, guarde para a newsletter e pergunte ao editor-chefe.
- Monte os posts com `"revisado": false` e mande a prévia ao editor-chefe; nada sai sem a revisão dele.

## O que nunca fazer

- Publicar ou enviar qualquer coisa sem a aprovação do editor-chefe.
- Inventar dado, número, citação ou fonte.
- Copiar texto de outra publicação: reescreva com suas palavras e cite.
- Colocar e-mail ou dado pessoal de inscritos no repositório (ele é público).
- Mexer nos segredos e variáveis do GitHub.
