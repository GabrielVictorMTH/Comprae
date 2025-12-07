from repo import categoria_repo
from model.categoria_model import Categoria


def main():
    print('Criando/verificando tabela categoria...')
    categoria_repo.criar_tabela()
    print('Inserindo categoria de teste...')
    cat = Categoria(nome='TesteAutomatizado', descricao='Inserida por script de teste')
    resultado = categoria_repo.inserir(cat)
    if resultado:
        print(f"Categoria inserida com ID: {resultado.id}")
    else:
        print('Falha ao inserir categoria')

    todas = categoria_repo.obter_todos()
    print(f'Total de categorias no banco: {len(todas)}')


if __name__ == '__main__':
    main()
