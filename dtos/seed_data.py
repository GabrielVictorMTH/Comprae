def inicializar_dados():
    """Inicializa dados básicos no banco"""
    # ... código existente de usuários ...

    # Categorias
    from repo import categoria_repo
    from model.categoria_model import Categoria

    if not categoria_repo.obter_todos():
        categorias = [
            Categoria(0, "Eletrônicos", "Produtos eletrônicos e tecnologia"),
            Categoria(0, "Livros", "Livros novos e usados"),
            Categoria(0, "Móveis", "Móveis e decoração"),
            Categoria(0, "Vestuário", "Roupas, calçados e acessórios"),
        ]
        for cat in categorias:
            categoria_repo.inserir(cat)
        logger.info("Categorias seed criadas")