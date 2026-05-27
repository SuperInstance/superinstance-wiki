.PHONY: lint spell all

lint:
	@echo "Markdown lint..."
	@which markdownlint-cli2 >/dev/null 2>&1 || echo "Install: npm install -g markdownlint-cli2"
	@markdownlint-cli2 "**/*.md" --config .markdownlint.json 2>/dev/null || true

spell:
	@echo "Spell check..."
	@which typos >/dev/null 2>&1 || echo "Install: cargo install typos-cli"
	@typos 2>/dev/null || true

all: lint spell
