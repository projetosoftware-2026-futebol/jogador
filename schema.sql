CREATE TABLE jogadores (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(120) NOT NULL,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 100),
  posicao VARCHAR(3) NOT NULL CHECK (
    posicao IN ('ATA', 'PD', 'PE', 'MC', 'LD', 'LE', 'ZAG', 'GOL')
  ),
  valor INTEGER NOT NULL CHECK (valor > 0),
  status VARCHAR(20) NOT NULL DEFAULT 'DISPONIVEL' CHECK (
    status IN ('DISPONIVEL', 'COMPRADO')
  ),
  liga VARCHAR(120) NOT NULL,
  clube_id INTEGER NULL
);
