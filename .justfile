# Use the just command runner to execute recipes: https://github.com/casey/just

set dotenv-load := false

_default:
    @just --list

fmt:
    poetry run black velosafe
    poetry run isort velosafe

lint: 
    poetry run ruff velosafe

