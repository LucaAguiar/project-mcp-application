-- Script para criar a tabela de formações e inserir dados fictícios, podendo ser executado em um banco de dados PostgreSQL.
-- Certifique-se de que o banco de dados esteja configurado corretamente antes de executar este script
-- e que você tenha as permissões necessárias para criar tabelas e inserir dados. Ou execute diretamente no pgAdmin(Recomendado).
DROP TABLE IF EXISTS formacoes;

CREATE TABLE formacoes (
    id SERIAL PRIMARY KEY,
    colaborador_id INT,
    nome TEXT,
    curso TEXT,
    status TEXT, -- concluído, em andamento, pendente
    data_inicio DATE,
    data_fim DATE
);

-- Dados fictícios
INSERT INTO formacoes (colaborador_id, nome, curso, status, data_inicio, data_fim) VALUES
(1, 'Charlie Chaplin', 'LGPD Básico', 'concluído', '2023-01-10', '2023-01-15'),
(2, 'Alice Wonderland', 'Atendimento ao Cliente', 'em andamento', '2025-05-01', NULL),
(3, 'Bob The Builder', 'Excel Avançado', 'concluído', '2024-09-10', '2024-10-01'),
(4, 'João da Silva', 'Comunicação Eficaz', 'concluído', '2024-03-05', '2024-03-15'),
(5, 'Carlos Eduardo', 'Liderança Estratégica', 'concluído', '2023-08-01', '2023-08-20'),
(5, 'Carlos Eduardo', 'Gestão de Projetos', 'em andamento', '2025-04-10', NULL),
(6, 'Maria Fernanda', 'Introdução ao Marketing Digital', 'pendente', '2025-06-01', NULL);

