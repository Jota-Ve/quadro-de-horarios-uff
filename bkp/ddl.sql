-- --------------------------------------------------------
-- Servidor:                     127.0.0.1
-- Versão do servidor:           11.6.2-MariaDB - mariadb.org binary distribution
-- OS do Servidor:               Win64
-- HeidiSQL Versão:              12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Copiando estrutura do banco de dados para quadro_de_horarios_uff
CREATE DATABASE IF NOT EXISTS `quadro_de_horarios_uff` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `quadro_de_horarios_uff`;

-- Copiando estrutura para tabela quadro_de_horarios_uff.curso
CREATE TABLE IF NOT EXISTS `curso` (
  `id` smallint(6) NOT NULL,
  `nome` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `curso_nome_IDX` (`nome`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela quadro_de_horarios_uff.disciplina
CREATE TABLE IF NOT EXISTS `disciplina` (
  `codigo` char(8) NOT NULL,
  `nome` varchar(100) NOT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela quadro_de_horarios_uff.horario
CREATE TABLE IF NOT EXISTS `horario` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `dia` enum('Segunda','Terca','Quarta','Quinta','Sexta','Sabado') NOT NULL,
  `inicio` time NOT NULL,
  `fim` time NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_horario_unico` (`dia`,`inicio`,`fim`)
) ENGINE=InnoDB AUTO_INCREMENT=1153 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela quadro_de_horarios_uff.horarioturma
CREATE TABLE IF NOT EXISTS `horarioturma` (
  `turma_id` bigint(20) NOT NULL,
  `horario_id` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`turma_id`,`horario_id`),
  KEY `fk_ht_horario` (`horario_id`),
  CONSTRAINT `fk_ht_horario` FOREIGN KEY (`horario_id`) REFERENCES `horario` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_ht_turma` FOREIGN KEY (`turma_id`) REFERENCES `turma` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela quadro_de_horarios_uff.ofertadevagas
CREATE TABLE IF NOT EXISTS `ofertadevagas` (
  `turma_id` bigint(20) NOT NULL,
  `curso_id` smallint(6) NOT NULL,
  `qtd_oferta_regular` tinyint(3) unsigned NOT NULL,
  `qtd_oferta_vestibular` tinyint(3) unsigned NOT NULL,
  `qtd_inscritos_regular` tinyint(3) unsigned NOT NULL,
  `qtd_inscritos_vestibular` tinyint(3) unsigned NOT NULL,
  `excedentes` tinyint(3) unsigned NOT NULL,
  `candidatos` tinyint(3) unsigned NOT NULL COMMENT '??',
  PRIMARY KEY (`turma_id`,`curso_id`),
  KEY `FK_ofertadevagas_curso` (`curso_id`),
  CONSTRAINT `FK_ofertadevagas_curso` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `FK_ofertadevagas_turma` FOREIGN KEY (`turma_id`) REFERENCES `turma` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela quadro_de_horarios_uff.professor
CREATE TABLE IF NOT EXISTS `professor` (
  `siape` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  PRIMARY KEY (`siape`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela quadro_de_horarios_uff.turma
CREATE TABLE IF NOT EXISTS `turma` (
  `id` bigint(20) NOT NULL,
  `nome` char(2) NOT NULL,
  `tipo_de_oferta` tinytext DEFAULT NULL,
  `carga_horaria` tinyint(3) unsigned DEFAULT NULL,
  `ano` smallint(5) unsigned NOT NULL,
  `semestre` tinyint(3) unsigned NOT NULL CHECK (`semestre` in (1,2)),
  `disciplina_cod` char(8) NOT NULL,
  `professor_siape` int(11) DEFAULT NULL,
  `url` char(65) GENERATED ALWAYS AS (concat('https://app.uff.br/graduacao/quadrodehorarios/turmas/',`id`)) VIRTUAL,
  PRIMARY KEY (`id`),
  KEY `fk_turma_disciplina` (`disciplina_cod`),
  KEY `fk_turma_professor` (`professor_siape`),
  CONSTRAINT `fk_turma_disciplina` FOREIGN KEY (`disciplina_cod`) REFERENCES `disciplina` (`codigo`) ON UPDATE CASCADE,
  CONSTRAINT `fk_turma_professor` FOREIGN KEY (`professor_siape`) REFERENCES `professor` (`siape`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Exportação de dados foi desmarcado.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
