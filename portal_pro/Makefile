# Variables
DOCS_DIR = docs
MAN_FILE = portal_pro.1
MD_FILE = $(DOCS_DIR)/$(MAN_FILE).md

# Default target
all: man

# Build the man page
man:
	@echo "Building man page..."
	pandoc $(MD_FILE) -s -t man -o $(MAN_FILE)
	@echo "Done. View with: man ./$(MAN_FILE)"

# Clean up
clean:
	rm -f $(MAN_FILE)

.PHONY: all man clean
