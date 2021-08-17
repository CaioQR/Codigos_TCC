###################################################################################################################################
###################################################################################################################################
################################################################### READ ME #######################################################
###################################################################################################################################
###################################################################################################################################

Dito isso, o código inicia-se com a leitura de uma imagem de um dos grupos da bandeja.
De OpenCV, utiliza-se o método imread(), sendo o diretório da imagem o primeiro parâmetro e o segundo 1 ou 0 para importá-la colorida ou em escala cinza, respectivamente.

A seguir, é necessário filtrar o background da imagem, ou seja, deseja-se reconhecer apenas os círculos e eliminar o restante.
Com a função split() separa-se a imagem cinza em canais RGB e então, para cada canal da imagem, realiza-se uma transformação morfológica de dilatação com dilate() e kernel de 10x10, juntando espaços quebrados pelo split() e consequentemente aumentando o objeto.
A imagem dilatada é suavizado a partir de sua mediana com medianblur(), o resultado é entendido como background da imagem em questão. Portanto, a folha e o círculo branco chamado aqui de célula será nada mais do que a diferença de 255 bits do canal pelo seu fundo (background) com medianBlur().
Antes de juntar os canais novamente em uma lista “result_norm_planes”, é importante normalizá-los em uma escala 0 a 255 bits. Agora, fora do laço condicional for, o vetor é transformado de volta como imagem em merge() e seu threshold é definido automaticamente pelo método binário invertido e adaptado com algoritmo Otsu [6].

o algoritmo deve ser capaz então de identificar os círculos da bandeja a fim de nomeá-los por grupo (A - H) e célula (1 - 16) e facilitar sua posterior identificação.
A biblioteca OpenCV disponibiliza a função HoughCircles() para identificar formas geométricas.
Passamos com argumentos a imagem em escala cinza, método de Transformada de Hough [7 e 8], a razão inversa “dp” da resolução do acumulador em relação a imagem – ou seja, basicamente a sensibilidade da função, sendo o melhor valor geralmente entre 1 e 2 e testado na prática –, mínima distância ideal entre cada círculo e intervalo limite do raio.
Também foi inserido um filtro de borda Canny [9] em “param1” e “param2” como limite do acumulador, isto é, a confiabilidade mínima de um círculo detectado a fim de evitar falsos positivos ou negativos.

O algoritmo de Canny, desenvolvido por John F. Canny em 1986, tem como finalidade detectar bordas em uma imagem complexa, por vezes com imperfeições e diferentes rugosidades, tarefa esta trabalhosa para algoritmos mais simples.
A teoria de Canny consiste em aplicar um filtro gaussiano para reduzir o ruído da imagem em análise, achar seu gradientes e reduzir a espessura das bordas. Por fim, aplica-se perturbações, histereses no sistema: o limite define o que é uma borda verdadeira e abaixo dele, os objetos podem ser removidos da imagem.
O resultado é uma lista de coordenadas e raio de cada círculo.

Essa lista é salva em um dataframe, contendo também um index de seu respectivo grupo e célula.Utilizando as coordenadas, agora é possível iterar entre círculo e exibi-los na imagem

Dessa forma foi possível, com uma única imagem por grupo da bandeja, recortar cada círculo para processamento, realizando o cálculo de áreas separadamente.
Essa metodologia provou ser tão efetiva quanto a captura de imagem individual, caso a câmera percorresse cada amostra do ensaio, além de também armazenar um arquivo de imagem .jpg para cada amostra para posterior análise e validação pelo usuário no sistema.
Finalizado a captura e recorte de cada célula da bandeja, o sistema parte para a identificação de objetos (bandeja, planta, lagarta e excremento), dessa vez operando com a biblioteca Scikit Image.
O código varre cada folha arquivada no diretório do ensaio, aplica novamente um threshold de Otsu e com a imagem já filtrada, rotula os diferentes objetos e regiões pela função label().

Finalmente, aplica-se a função regionprops() do próprio Scikit Image, a qual irá retornar a área e diâmetro aproximado de cada região.
Considerando uma escala de 0,6 micrômetros para cada pixel, calcula-se a área e diâmetro equivalentes.
Convenientemente, os dados obtidos são salvos em um arquivo padrão .csv similar à tabela abaixo, formando uma base de dados no diretório para o usuário consultar no futuro.