# Plaquet.AI
Local onde o sistema clinico que contem a Inteligência Artificial Plaquet.AI está sendo desenvolvido
Detalhamento das Pastas
data/

raw/: Aqui vão ficar os dados brutos, como imagens originais e as anotações brutas. Não suba arquivos muito grandes para o GitHub, use um serviço de armazenamento em nuvem, caso necessário.
processed/: Aqui você pode armazenar as imagens processadas, como imagens redimensionadas, ou as anotações convertidas no formato correto para treinar o modelo.
external/: Caso você tenha algum modelo pré-treinado ou arquivos de dados externos, como modelos do YOLO, pode armazenar aqui.
models/

yolov5/ e yolov8/: Aqui você pode salvar os modelos treinados, como os arquivos .pt do YOLOv5 ou YOLOv8. Esses arquivos são grandes e não devem ser subidos para o GitHub, mas podem ser armazenados em algum serviço de nuvem e os links podem ser incluídos no repositório.
config/: Arquivos de configuração do modelo, como o .yaml com os parâmetros de treinamento.
notebooks/

Os notebooks são úteis para protótipos, análise de dados, ou até treinamento de modelos de forma interativa. No Jupyter, você pode ir experimentando o processo de contagem de plaquetas enquanto escreve o código e analisa os resultados.
src/

data_preprocessing/: Aqui ficam os scripts para processar os dados, como redimensionamento de imagens, conversão de anotações (de JSON para YOLO, por exemplo), limpeza de dados, etc.
model_training/: Aqui ficam os scripts para treinar o modelo, por exemplo, a parte onde você treina o modelo YOLO para reconhecer plaquetas.
model_inference/: Este diretório pode conter scripts de inferência, ou seja, como usar o modelo treinado para detectar as plaquetas nas imagens.
utils/: Funções utilitárias que você pode precisar em diversas partes do código, como funções para verificar se diretórios existem, ou para processar os dados.
requirements.txt

Contém as dependências que o projeto precisa, como torch, opencv-python, numpy, yolov5, etc. Esse arquivo permite que qualquer pessoa que pegue o repositório consiga instalar todas as dependências necessárias.
.gitignore

Especifica quais arquivos e pastas não devem ser versionados pelo Git, como pastas de ambientes virtuais (venv/), dados grandes ou temporários (logs, pastas de treinamento), etc.
README.md

O arquivo de documentação que descreve o projeto, como configurá-lo, o que o modelo faz, como rodá-lo, etc.
LICENSE

Aqui você coloca a licença do seu projeto, como a licença proprietária ou outra, caso tenha definido uma.