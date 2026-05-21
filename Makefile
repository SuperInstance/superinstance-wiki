MAKEFILE for the wiki

.PHONY: regenerate serve lint clean help

help:
	@echo "SuperInstance Wiki — make targets"
	@echo ""
	@echo "  make regenerate   — Refresh all indexes from live GitHub data"
	@echo "  make serve          — Start local HTTP server for index.html"
	@echo "  make lint           — Check markdown links and formatting"
	@echo "  make clean          — Remove generated files"
	@echo "  make push           — Commit and push changes"
	@echo "  make stats          — Show repo counts and health summary"

regenerate:
	python3 scripts/regenerate-triage.py

serve:
	python3 -m http.server 8000

lint:
	@echo "Checking markdown..."
	@which markdownlint 2>/dev/null || echo "Install markdownlint-cli: npm install -g markdownlint-cli"
	markdownlint *.md CHRONICLE/*.md INDEXES/*.md || true

clean:
	rm -f data/all-repos.csv data/repos.json
	@echo "Generated data removed. Run 'make regenerate' to rebuild."

push:
	git add -A
	git commit -m "Wiki update — $(shell date -u +%Y-%m-%d)" || true
	git push origin main

stats:
	@echo "=== Fleet Stats ==="
	@python3 -c "import json; d=json.load(open('data/repos.json')); print(f'Total: {d[\"total\"]}'); print(f'KEEP: {len([r for r in d[\"repos\"] if r[\"action\"]==\"KEEP\"])}'); print(f'PRIVATE: {len([r for r in d[\"repos\"] if r[\"action\"]==\"PRIVATE\"])}'); print(f'ARCHIVE: {len([r for r in d[\"repos\"] if r[\"action\"]==\"ARCHIVE\"])}'); print(f'MONITOR: {len([r for r in d[\"repos\"] if r[\"action\"]==\"MONITOR\"])}')"
