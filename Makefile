OBS_PROJECT := EA4
OBS_PACKAGE := scl-php71-meta
DISABLE_BUILD := repository=CentOS_8 repository=CentOS_9
include $(EATOOLS_BUILD_DIR)obs.mk
