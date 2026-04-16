#!/bin/bash

# Script de Backup Automático para o GitHub
# Este script salva o banco de dados SQLite no repositório.

echo "Iniciando backup do banco de dados..."

# Adiciona o arquivo do banco de dados
git add db.sqlite3

# Cria o commit com data e hora
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "Backup do Banco de Dados: $TIMESTAMP"

# Tenta enviar para o GitHub (o remoto 'origin' deve estar configurado)
if git push origin main; then
    echo "Sucesso: Backup enviado para o GitHub!"
else
    echo "Erro: Não foi possível enviar para o GitHub. Verifique se o 'origin' está configurado."
fi
