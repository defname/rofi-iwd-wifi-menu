# Makefile just for installation/uninstallation and cleanup

# Filepaths of all project files that should be installed
SRC_FILES := README.md $(shell echo *.py iwdrofimenu/*.py) $(shell find res -type f -not -name "*.svg")
# Filepath of the executable
EXE_FILE := iwdrofimenu.py
# Name for the symlink created in $(INSTALLPATH)/bin
LINK_NAME := iwdrofimenu
# Name of the subdirectory to install
PKG_NAME := iwdrofimenu

# Where to install
ifeq ($(PREFIX),)
	#PREFIX := /tmp
	PREFIX := /usr
endif

SHARE_SUBDIR := share
BIN_SUBDIR := bin

INSTALL_DIR := $(DESTDIR)$(PREFIX)/$(SHARE_SUBDIR)/$(PKG_NAME)
BIN_DIR := $(DESTDIR)$(PREFIX)/$(BIN_SUBDIR)

# Filepaths of all installed files
DEST_FILES := $(patsubst %, $(INSTALL_DIR)/%, $(SRC_FILES))

default:
	@cat INSTALL 

$(DEST_FILES): 
	install -D -m 644 $(patsubst $(INSTALL_DIR)/%,%,$@) $@

install: $(DEST_FILES)
	ln -s $(INSTALL_DIR)/$(EXE_FILE) $(BIN_DIR)/$(LINK_NAME)
	chmod 755 $(INSTALL_DIR)/$(EXE_FILE)

uninstall:
	rm -rf $(INSTALL_DIR)
	rm $(BIN_DIR)/$(LINK_NAME)

update: uninstall install

clean:
	rm -r __pycache__
	rm -r iwdrofimenu/__pycache__

.PHONY: default
