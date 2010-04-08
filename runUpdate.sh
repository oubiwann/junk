#!/bin/bash

# Parameters.
PASSWORD=$1

# Configuration.
USER="duncan@ubuntu.com"
DATE="2010-04-08"
MILESTONE="ubuntu-10.04-beta-2"
REAL_PAGE="ReleaseTeam/FeatureStatus/Ubuntu10.04Beta2Postponed"

TEST_PAGE="Oubiwann/TestPage"
BASE_WIKI="https://wiki.ubuntu.com"
BASE_DIR="/Users/oubiwann/lab/platform-scripts"
#BASE_DIR="/home/oubiwann/lab/platform-scripts"
DB_SOURCE="http://people.canonical.com/~pitti/workitems"
DB_NAME="lucid.db"

function abort() {
    MSG=$1
    echo $MSG
    echo "Exiting ..."
    echo
    exit 1
}

# Parameter check.
if [[ -z $PASSWORD ]]; then
    echo
    abort "No Launchpad password supplied."
fi

# Remove the old database and get the new one.
rm lucid.db
wget ${DB_SOURCE}/${DB_NAME}

# Perform a dry-run, updating a test page.
./updateDropped.py -u $USER -p $PASSWORD \
    -d ${BASE_DIR}/${DB_NAME} --url ${BASE_WIKI}/${TEST_PAGE} \
    --trivial --date $DATE --milestone $MILESTONE

echo "Check out your test page here:"
echo "  ${BASE_WIKI}/${TEST_PAGE}."
echo "If there are any problems, hit ^C now and exit this script."
echo "Otherwise, hit ENTER."
read NULL

# Once everything looks cool, do the real thing.
./updateDropped.py -u $USER -p $PASSWORD \
    -d ${BASE_DIR}/${DB_NAME} --url ${BASE_WIKI}/${REAL_PAGE} \
    --date $DATE --milestone $MILESTONE

echo "Your page is viewable here:"
echo "  ${BASE_WIKI}/${REAL_PAGE}"
