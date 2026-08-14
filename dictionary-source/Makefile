#
# Makefile
#
#
#

###########################

# You need to edit these values.

DICT_NAME		=	"ECDICT 简明英汉字典"
DICT_SRC_PATH		=	ECDICT-styled.xml
CSS_PATH		=	MyDictionary.css
PLIST_PATH		=	MyInfo.plist
XSL_PATH		=	MyDictionary.xsl
PREFS_PATH		=	MyDictionary_prefs.html
IMAGE_PATH		=	Images/_internal_dictionary.png

DICT_BUILD_OPTS		=	-v 10.11
# Suppress adding supplementary key.
# DICT_BUILD_OPTS		=	-s 0	# Suppress adding supplementary key.

###########################

# The DICT_BUILD_TOOL_DIR value is used also in "build_dict.sh" script.
# You need to set it when you invoke the script directly.

DICT_BUILD_TOOL_DIR	=	"/Applications/Utilities/Dictionary Development Kit"
DICT_BUILD_TOOL_BIN	=	"$(DICT_BUILD_TOOL_DIR)/bin"

###########################

DICT_DEV_KIT_OBJ_DIR	=	./objects
export	DICT_DEV_KIT_OBJ_DIR

DESTINATION_FOLDER	=	~/Library/Dictionaries
RM			=	/bin/rm

###########################

all:
	"$(DICT_BUILD_TOOL_BIN)/build_dict.sh" $(DICT_BUILD_OPTS) $(DICT_NAME) $(DICT_SRC_PATH) $(CSS_PATH) $(PLIST_PATH)
	ditto --noextattr --norsrc $(XSL_PATH) $(DICT_DEV_KIT_OBJ_DIR)/$(DICT_NAME).dictionary/Contents/Resources/$(XSL_PATH)
	ditto --noextattr --norsrc $(PREFS_PATH) $(DICT_DEV_KIT_OBJ_DIR)/$(DICT_NAME).dictionary/Contents/Resources/$(PREFS_PATH)
	mkdir -p $(DICT_DEV_KIT_OBJ_DIR)/$(DICT_NAME).dictionary/Contents/Resources/Images
	ditto --noextattr --norsrc $(IMAGE_PATH) $(DICT_DEV_KIT_OBJ_DIR)/$(DICT_NAME).dictionary/Contents/Resources/$(IMAGE_PATH)
	echo "Done."


install:
	echo "Installing into $(DESTINATION_FOLDER)".
	mkdir -p $(DESTINATION_FOLDER)
	ditto --noextattr --norsrc $(DICT_DEV_KIT_OBJ_DIR)/$(DICT_NAME).dictionary  $(DESTINATION_FOLDER)/$(DICT_NAME).dictionary
	touch $(DESTINATION_FOLDER)
	echo "Done."
	echo "To test the new dictionary, try Dictionary.app."

clean:
	$(RM) -rf $(DICT_DEV_KIT_OBJ_DIR)
