# BBI Stats

Este é um repositório onde juntei o útil ao agradável. Para fixar melhor o conteúdo de Django, fiz um servidor que pega os resultados do futebol inglês na temporada e a partir dali gera estatísticas, tabela, e o que mais for interessante para depois gerar posts para a página Bate-Bola Inglês, que está em várias redes sociais como Instagram, Facebook e Twitter sob o nome @BBIngles.

## Como rodar

- Tenha instalado o Python
- Tenha instalado o Django

~~~
pip install django
~~~

- Aplique as migrações e rode o servidor
~~~
python manage.py migrate
python manage.py runserver
~~~

## Bibliotecas utilizadas
Pandas - para formar as tabelas e conseguir retornar as estatísticas relevantes.


## Próximos passos
Pretendo incluir: 
- Melhor ataque
- Melhor defesa
- Tabela de melhores mandantes
- Tabela de melhores visitantes

### Observações
Não sou o mais aplicado em frontend, então se quiser fazer um branch no projeto e fazer uma reforma visual, fique à vontade!
